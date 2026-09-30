# [?] fix: docker/src/docker/DockerfileAL to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2024-07-27
Source: https://github.com/corda/corda/commit/ca7cf73ceb1a897221e3c3db4e029d3c07e2f909
Type: security-commit

## Details
fix: docker/src/docker/DockerfileAL to reduce vulnerabilities

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-AMZN2-CPIO-6371135
- https://snyk.io/vuln/SNYK-AMZN2-GLIBCMINIMALLANGPACK-6745170
- https://snyk.io/vuln/SNYK-AMZN2-LIBNGHTTP2-6745071
- https://snyk.io/vuln/SNYK-AMZN2-NSS-6229002
- https://snyk.io/vuln/SNYK-AMZN2-NSSTOOLS-6229107

## Patch
### docker/src/docker/DockerfileAL
```diff
@@ -1,4 +1,4 @@
-FROM amazoncorretto:8u392-al2
+FROM amazoncorretto:8u422-al2
 
 ## Add packages, clean cache, create dirs, create corda user and change ownership
 RUN yum -y install bash && \
```
