# [?] fix: Temporarily use our go-libp2p-pubsub fork to avoid deadlock during shutdown (#3064)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-08-18
Source: https://github.com/NethermindEth/juno/commit/0ef3ab39fb4ec2ae6f5fa6306777847cd9f14392
Type: security-commit

## Details
fix: Temporarily use our go-libp2p-pubsub fork to avoid deadlock during shutdown (#3064)

fix: Temporarily use our go-libp2p-pubsub fork to avoid deadlock

## Patch
### go.mod
```diff
@@ -19,7 +19,7 @@ require (
 	github.com/go-playground/validator/v10 v10.27.0
 	github.com/libp2p/go-libp2p v0.43.0
 	github.com/libp2p/go-libp2p-kad-dht v0.34.0
-	github.com/libp2p/go-libp2p-pubsub v0.14.1
+	github.com/libp2p/go-libp2p-pubsub v0.14.2
 	github.com/mitchellh/mapstructure v1.5.0
 	github.com/multiformats/go-multiaddr v0.16.1
 	github.com/olekukonko/tablewriter v1.0.9
@@ -195,3 +195,5 @@ require (
 )
 
 replace github.com/starknet-io/starknet-p2pspecs => ./starknet-p2pspecs
+
+replace github.com/libp2p/go-libp2p-pubsub v0.14.2 => github.com/infrmtcs/go-libp2p-pubsub v0.0.0-20250818055235-0d5c6026369b
```

### go.sum
```diff
@@ -219,6 +219,8 @@ github.com/influxdata/influxdb1-client v0.0.0-20220302092344-a9ab5670611c h1:qSH
 github.com/influxdata/influxdb1-client v0.0.0-20220302092344-a9ab5670611c/go.mod h1:qj24IKcXYK6Iy9ceXlo3Tc+vtHo9lIhSX5JddghvEPo=
 github.com/influxdata/line-protocol v0.0.0-20200327222509-2487e7298839 h1:W9WBk7wlPfJLvMCdtV4zPulc4uCPrlywQOmbFOhgQNU=
 github.com/influxdata/line-protocol v0.0.0-20200327222509-2487e7298839/go.mod h1:xaLFMmpvUxqXtVkUJfg9QmT88cDaCJ3ZKgdZ78oO8Qo=
+github.com/infrmtcs/go-libp2p-pubsub v0.0.0-20250818055235-0d5c6026369b h1:Yc26HbZ0UGlyQJDuwNyD6XKQy+SguaywHPOR9SdMsMU=
+github.com/infrmtcs/go-libp2p-pubsub v0.0.0-20250818055235-0d5c6026369b/go.mod h1:MKPU5vMI8RRFyTP0HfdsF9cLmL1nHAeJm44AxJGJx44=
 github.com/ipfs/boxo v0.33.1 h1:89m+ksw+cYi0ecTNTJ71IRS5ZrLiovmO6XWHIOGhAEg=
 github.com/ipfs/boxo v0.33.1/go.mod h1:KwlJTzv5fb1GLlA9KyMqHQmvP+4mrFuiE3PnjdrPJHs=
 github.com/ipfs/go-block-format v0.2.2 h1:uecCTgRwDIXyZPgYspaLXoMiMmxQpSx2aq34eNc4YvQ=
@@ -281,8 +283,6 @@ github.com/libp2p/go-libp2p-kad-dht v0.34.0 h1:yvJ/Vrt36GVjsqPxiGcuuwOloKuZLV9Aa
 github.com/libp2p/go-libp2p-kad-dht v0.34.0/go.mod h1:JNbkES4W5tajS6uYivw6MPs0842cPHAwhgaPw8sQG4o=
 github.com/libp2p/go-libp2p-kbucket v0.8.0 h1:QAK7RzKJpYe+EuSEATAaaHYMYLkPDGC18m9jxPLnU8s=
 github.com/libp2p/go-libp2p-kbucket v0.8.0/go.mod h1:JMlxqcEyKwO6ox716eyC0hmiduSWZZl6JY93mGaaqc4=
-github.com/libp2p/go-libp2p-pubsub v0.14.1 h1:XK/rPKZKhPvRrtsjvfwrOZPnQQbGLmaEg7u6qnJfn8U=
-github.com/libp2p/go-libp2p-pubsub v0.14.1/go.mod h1:MKPU5vMI8RRFyTP0HfdsF9cLmL1nHAeJm44AxJGJx44=
 github.com/libp2p/go-libp2p-record v0.3.1 h1:cly48Xi5GjNw5Wq+7gmjfBiG9HCzQVkiZOUZ8kUl+Fg=
 github.com/libp2p/go-libp2p-record v0.3.1/go.mod h1:T8itUkLcWQLCYMqtX7Th6r7SexyUJpIyPgks757td/E=
 github.com/libp2p/go-libp2p-routing-helpers v0.7.5 h1:HdwZj9NKovMx0vqq6YNPTh6aaNzey5zHD7HeLJtq6fI=
```
