# [?] fix: docker/Dockerfile to reduce vulnerabilities (#5620)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2024-11-05
Source: https://github.com/graphprotocol/graph-node/commit/cb3d85c527743dfca87799f7c0cf1b530adb8e93
Type: security-commit

## Details
fix: docker/Dockerfile to reduce vulnerabilities (#5620)

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-DEBIAN11-ZLIB-6008961
- https://snyk.io/vuln/SNYK-DEBIAN11-SYSTEMD-6277510
- https://snyk.io/vuln/SNYK-DEBIAN11-SYSTEMD-6277510
- https://snyk.io/vuln/SNYK-DEBIAN11-NCURSES-6252771
- https://snyk.io/vuln/SNYK-DEBIAN11-UTILLINUX-2401081

Co-authored-by: snyk-bot <snyk-bot@snyk.io>

## Patch
### docker/Dockerfile
```diff
@@ -52,7 +52,7 @@ COPY docker/Dockerfile /Dockerfile
 COPY docker/bin/* /usr/local/bin/
 
 # The graph-node runtime image with only the executable
-FROM debian:bullseye-slim as graph-node
+FROM debian:bookworm-20240722-slim as graph-node
 ENV RUST_LOG ""
 ENV GRAPH_LOG ""
 ENV EARLY_LOG_CHUNK_SIZE ""
```
