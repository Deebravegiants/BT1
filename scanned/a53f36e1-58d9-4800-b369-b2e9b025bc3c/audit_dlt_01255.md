# [?] torrent: cherry-pick from r31 to fix panic on index out of range in torrent lib (#17190)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-09-22
Source: https://github.com/erigontech/erigon/commit/cb9db1ece65494fedaf819180f45fe22c7bac925
Type: security-commit

## Details
torrent: cherry-pick from r31 to fix panic on index out of range in torrent lib (#17190)

cherry-pick of https://github.com/erigontech/erigon/pull/16990 since I
run into the same panic in `main` while running tests

## Patch
### go.mod
```diff
@@ -29,7 +29,7 @@ require (
 	github.com/anacrolix/go-libutp v1.3.2
 	github.com/anacrolix/log v0.17.0
 	github.com/anacrolix/missinggo/v2 v2.10.0
-	github.com/anacrolix/torrent v1.59.2-0.20250831024100-5a4e71ecb3c3
+	github.com/anacrolix/torrent v1.59.2-0.20250903105451-d922d78d2e61
 	github.com/c2h5oh/datasize v0.0.0-20231215233829-aa82cc1e6500
 	github.com/cenkalti/backoff/v4 v4.3.0
 	github.com/charmbracelet/bubbles v0.21.0
```

### go.sum
```diff
@@ -143,8 +143,8 @@ github.com/anacrolix/sync v0.5.4/go.mod h1:21cUWerw9eiu/3T3kyoChu37AVO+YFue1/H15
 github.com/anacrolix/tagflag v0.0.0-20180109131632-2146c8d41bf0/go.mod h1:1m2U/K6ZT+JZG0+bdMK6qauP49QT4wE5pmhJXOKKCHw=
 github.com/anacrolix/tagflag v1.0.0/go.mod h1:1m2U/K6ZT+JZG0+bdMK6qauP49QT4wE5pmhJXOKKCHw=
 github.com/anacrolix/tagflag v1.1.0/go.mod h1:Scxs9CV10NQatSmbyjqmqmeQNwGzlNe0CMUMIxqHIG8=
-github.com/anacrolix/torrent v1.59.2-0.20250831024100-5a4e71ecb3c3 h1:BVmTbvrRJ81R5mFR1kX3TPNs8WsZQDRJ0+hsIAn7RNQ=
-github.com/anacrolix/torrent v1.59.2-0.20250831024100-5a4e71ecb3c3/go.mod h1:6hGL5nOAk4j0zrPqyZ7GKYIkRPgehXFE9N8N6rAatQI=
+github.com/anacrolix/torrent v1.59.2-0.20250903105451-d922d78d2e61 h1:86zuTAMse1rzLq6hSGHad8gdZ0I4JRhFUuvZggvByMQ=
+github.com/anacrolix/torrent v1.59.2-0.20250903105451-d922d78d2e61/go.mod h1:6hGL5nOAk4j0zrPqyZ7GKYIkRPgehXFE9N8N6rAatQI=
 github.com/anacrolix/upnp v0.1.4 h1:+2t2KA6QOhm/49zeNyeVwDu1ZYS9dB9wfxyVvh/wk7U=
 github.com/anacrolix/upnp v0.1.4/go.mod h1:Qyhbqo69gwNWvEk1xNTXsS5j7hMHef9hdr984+9fIic=
 github.com/anacrolix/utp v0.1.0 h1:FOpQOmIwYsnENnz7tAGohA+r6iXpRjrq8ssKSre2Cp4=
```
