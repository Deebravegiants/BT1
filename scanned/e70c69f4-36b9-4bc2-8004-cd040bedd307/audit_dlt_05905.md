# [?] fix: release-tools/testing/requirements.txt to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2025-06-16
Source: https://github.com/corda/corda/commit/9581001de59c8bc84b3361257bdc776ce8c97e38
Type: security-commit

## Details
fix: release-tools/testing/requirements.txt to reduce vulnerabilities


The following vulnerabilities are fixed by pinning transitive dependencies:
- https://snyk.io/vuln/SNYK-PYTHON-REQUESTS-10305723

## Patch
### release-tools/testing/requirements.txt
```diff
@@ -2,5 +2,5 @@ jira==2.0.0
 keyring==13.1.0
 termcolor==1.1.0
 urllib3>=2.2.2 # not directly required, pinned by Snyk to avoid a vulnerability
-requests>=2.32.2 # not directly required, pinned by Snyk to avoid a vulnerability
+requests>=2.32.4 # not directly required, pinned by Snyk to avoid a vulnerability
 setuptools>=70.0.0 # not directly required, pinned by Snyk to avoid a vulnerability
```
