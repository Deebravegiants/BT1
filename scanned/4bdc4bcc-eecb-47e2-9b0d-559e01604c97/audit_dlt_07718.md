# [?] Fix vulnerabilities from openjdk-11 base image (#2452)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2021-06-24
Source: https://github.com/besu-eth/besu/commit/ddc95c4bd5a1076625cec825f8d6a5dba6ac706a
Type: security-commit

## Details
Fix vulnerabilities from openjdk-11 base image (#2452)

Signed-off-by: Juan Cruz <jmcruz1983@gmail.com>

## Patch
### docker/openjdk-11/Dockerfile
```diff
@@ -1,5 +1,6 @@
 
-FROM openjdk:11.0.7-jre-slim-buster
+FROM adoptopenjdk/openjdk11:jre-11.0.11_9
+
 ARG VERSION="dev"
 
 RUN adduser --disabled-password --gecos "" --home /opt/besu besu && \
```
