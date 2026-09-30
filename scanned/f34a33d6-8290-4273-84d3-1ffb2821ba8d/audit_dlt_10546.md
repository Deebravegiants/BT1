# [?] fix: release-tools/testing/requirements.txt to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2025-05-05
Source: https://github.com/corda/corda/commit/92438c3a001b18fb56a3cb68c631bdada67acb15
Type: security-commit

## Details
fix: release-tools/testing/requirements.txt to reduce vulnerabilities


The following vulnerabilities are fixed by pinning transitive dependencies:
- https://snyk.io/vuln/SNYK-PYTHON-SETUPTOOLS-9964606

## Patch
### release-tools/testing/requirements.txt
```diff
@@ -3,4 +3,4 @@ keyring==13.1.0
 termcolor==1.1.0
 urllib3>=2.2.2 # not directly required, pinned by Snyk to avoid a vulnerability
 requests>=2.32.2 # not directly required, pinned by Snyk to avoid a vulnerability
-setuptools>=70.0.0 # not directly required, pinned by Snyk to avoid a vulnerability
+setuptools>=78.1.1 # not directly required, pinned by Snyk to avoid a vulnerability
```
