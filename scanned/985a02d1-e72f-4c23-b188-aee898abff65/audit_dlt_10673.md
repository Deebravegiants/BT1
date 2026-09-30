# [?] fix: release-tools/testing/requirements.txt to reduce vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2024-08-01
Source: https://github.com/corda/corda/commit/bd901b5121d73f36ad37bce80d66265b6d655d93
Type: security-commit

## Details
fix: release-tools/testing/requirements.txt to reduce vulnerabilities


The following vulnerabilities are fixed by pinning transitive dependencies:
- https://snyk.io/vuln/SNYK-PYTHON-REQUESTS-6928867
- https://snyk.io/vuln/SNYK-PYTHON-SETUPTOOLS-3180412
- https://snyk.io/vuln/SNYK-PYTHON-SETUPTOOLS-7448482
- https://snyk.io/vuln/SNYK-PYTHON-URLLIB3-7267250

## Patch
### release-tools/testing/requirements.txt
```diff
@@ -2,5 +2,5 @@ jira==2.0.0
 keyring==13.1.0
 termcolor==1.1.0
 urllib3>=2.2.2 # not directly required, pinned by Snyk to avoid a vulnerability
-requests>=2.32.0 # not directly required, pinned by Snyk to avoid a vulnerability
+requests>=2.32.2 # not directly required, pinned by Snyk to avoid a vulnerability
 setuptools>=70.0.0 # not directly required, pinned by Snyk to avoid a vulnerability
```
