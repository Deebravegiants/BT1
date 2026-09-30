# [?] fix: docker/src/docker/DockerfileAL to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2026-01-29
Source: https://github.com/corda/corda/commit/f026569037153c8052a3c795f9baccad772dea78
Type: security-commit

## Details
fix: docker/src/docker/DockerfileAL to reduce vulnerabilities

## Patch
### docker/src/docker/DockerfileAL
```diff
@@ -1,4 +1,4 @@
-FROM amazoncorretto:17.0.17
+FROM amazoncorretto:17.0.18
 
 ## Add packages, clean cache, create dirs, create corda user and change ownership
 RUN yum -y install bash && \
```
