# [?] fix: docker/src/docker/DockerfileAL to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2025-02-02
Source: https://github.com/corda/corda/commit/a7701415eba79daff514f869be1192f51a80dd6d
Type: security-commit

## Details
fix: docker/src/docker/DockerfileAL to reduce vulnerabilities

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-AMZN2-EXPAT-8545078
- https://snyk.io/vuln/SNYK-AMZN2-CURL-8611959
- https://snyk.io/vuln/SNYK-AMZN2-GLIBC-8545261
- https://snyk.io/vuln/SNYK-AMZN2-GLIBCCOMMON-8545325
- https://snyk.io/vuln/SNYK-AMZN2-LIBCURL-8611960

## Patch
### docker/src/docker/DockerfileAL
```diff
@@ -1,4 +1,4 @@
-FROM amazoncorretto:8u422-al2
+FROM amazoncorretto:8u442-al2
 
 ## Add packages, clean cache, create dirs, create corda user and change ownership
 RUN yum -y install bash && \
```
