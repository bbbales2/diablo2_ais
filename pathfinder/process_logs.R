library(jsonlite)
library(tidyverse)
library(ggplot2)
library(rstan)
library(shinystan)

results <- lapply(strsplit(readLines("pathFinders/0.log")," "), fromJSON)

time = lapply(results, function(x) { x[[1]] })
state = lapply(results, function(x) { x[[2]] }) %>% enframe %>%
  mutate(isNull = map(value, is.null)) %>%
  unnest(isNull)
actions = lapply(results, function(x) { x[[3]] })

df = bind_cols(list(time = time) %>% as.tibble %>% unnest %>% mutate(time = time - min(time)),
               as.tibble(state %>% select(value, isNull)),
               matrix(unlist(actions), byrow = TRUE, ncol = 3) %>% as.tibble %>%
                rename(click = V1, x = V2, y = V3) %>%
                mutate(angle = atan2(237 - y, x - 325) * 180 / pi,
                   ca = as.integer(angle / 45)) %>%
                mutate(ca = ca + (ca < 0) * 8 + 1) %>% select(angle, ca)) %>%
  filter(isNull == FALSE) %>%
  mutate(x = map(value, 1), y = map(value, 2)) %>%
  unnest(x, y) %>%
  select(-isNull, -value)

goalx = 5600
goaly = 4800

minx = min(df$x)
maxx = max(df$x)
miny = min(df$y)
maxy = max(df$y)

dfs = df %>% mutate(score = -sqrt((x - goalx)^2 + (y - goaly)^2)) %>%
  mutate(reward = lead(score) - score,
         xr = x,
         yr = y,
         x = (x - min(x)) / 50.0,
         y = (y - min(y)) / 50.0) %>% drop_na

fit = stan("models/fit.stan", data = list(N = nrow(dfs),
                                          C = dfs %>% pull(ca) %>% unique %>% length,
                                          x = dfs$x,
                                          y = dfs$y,
                                          ca = dfs$ca,
                                          treward = dfs$reward), chains = 1,
                                          control = list(max_treedepth = 5), iter = 1000)

bind_cols(dfs, list(pca = extract(fit, "cat")$cat[10, ])) %>%
  mutate(angle = (pca - 1) * 180 / pi) %>% ggplot(aes(xr, yr)) +
  geom_spoke(aes(angle = angle, radius = 0.1), alpha = 0.2, arrow = arrow(length = unit(0.025, "npc")))

i = 200
list(xp = extract(fit, "xp")$xp[i,] * 50 + minx,
     yp = extract(fit, "yp")$yp[i,] * 50 + miny,
     cat = extract(fit, "cat")$cat[i,]) %>% as.tibble %>%
  mutate(angle = (cat - 1) * 180 / pi + pi) %>% ggplot(aes(xp, yp)) +
  geom_point(data = dfs, aes(xr, yr, color = reward)) +
  geom_spoke(aes(angle = angle, radius = 0.00025), arrow = arrow(length = unit(0.015, "npc")))


dfs %>% ggplot(aes(ca, reward)) +
  geom_point()

dfs %>% ggplot(aes(xr, yr)) +
  geom_point(aes(color = time))

t(results) %>% as.tibble

actions %>%
  enframe %>%
  mutate(x = map(value, function(x) x[[1]]))

  unlist(recursive = FALSE) %>% 
  enframe()
