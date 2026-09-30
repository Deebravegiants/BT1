# [?] fix: contrib/prototools-docker/Dockerfile to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2023-10-11
Source: https://github.com/neutron-org/neutron/commit/af469b4dd193a51bc7894a5d89e564cd3c19799d
Type: security-commit

## Details
fix: contrib/prototools-docker/Dockerfile to reduce vulnerabilities

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-ALPINE318-BUSYBOX-5890990
- https://snyk.io/vuln/SNYK-ALPINE318-BUSYBOX-5890990
- https://snyk.io/vuln/SNYK-ALPINE318-BUSYBOX-5890990
- https://snyk.io/vuln/SNYK-ALPINE318-OPENSSL-5776808
- https://snyk.io/vuln/SNYK-ALPINE318-OPENSSL-5788370

## Patch
### contrib/prototools-docker/Dockerfile
```diff
@@ -39,7 +39,7 @@ RUN GO111MODULE=on go get \
 
 RUN upx --lzma /usr/local/bin/*
 
-FROM golang:1.19.11-alpine
+FROM golang:1.20.9-alpine
 ENV LD_LIBRARY_PATH=/lib64:/lib
 
 WORKDIR /work
```
