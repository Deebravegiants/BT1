# [?] fix: Dockerfile.rust-poetry to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2022-01-13
Source: https://github.com/chainflip-io/chainflip-backend/commit/f7e4db8bac0d821a626571fc66d9c0b9b6c5b204
Type: security-commit

## Details
fix: Dockerfile.rust-poetry to reduce vulnerabilities

The following vulnerabilities are fixed with an upgrade:
- https://snyk.io/vuln/SNYK-DEBIAN11-GLIBC-1296898
- https://snyk.io/vuln/SNYK-DEBIAN11-GLIBC-1296898
- https://snyk.io/vuln/SNYK-DEBIAN11-GLIBC-1296898
- https://snyk.io/vuln/SNYK-DEBIAN11-GLIBC-1296898
- https://snyk.io/vuln/SNYK-DEBIAN11-PYTHON39-1290158

## Patch
### Dockerfile.rust-poetry
```diff
@@ -1,4 +1,4 @@
-FROM python:bullseye
+FROM python:3.11.0a3-slim-bullseye
 
 USER root
 
```
