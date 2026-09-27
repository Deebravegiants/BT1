# [M] Kubernetes kubectl cp Vulnerable to Symlink Attack

## Summary
Severity: Medium
Advisory: GHSA-6qfg-8799-r575
CVE: CVE-2019-11251
CWE: CWE-59, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-6qfg-8799-r575
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.13.10 <1.13.11
- Go: `k8s.io/kubernetes` — affected >=1.14.6 <1.14.7
- Go: `k8s.io/kubernetes` — affected >=1.15.3 <1.16.0

## Details
The Kubernetes kubectl cp command in versions 1.1-1.12, and versions prior to 1.13.11, 1.14.7, and 1.15.4 allows a combination of two symlinks provided by tar output of a malicious container to place a file outside of the destination directory specified in the kubectl cp invocation. This could be used to allow an attacker to place a nefarious file using a symlink, outside of the destination tree.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11251
- https://github.com/kubernetes/kubernetes/issues/87773
- https://github.com/kubernetes/kubernetes/pull/82143
- https://groups.google.com/d/msg/kubernetes-announce/YYtEFdFimZ4/nZnOezZuBgAJ
