# [C] Etcd-io Improper Authentication vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gmph-wf7j-9gcm
CVE: CVE-2021-28235
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-04
Source: https://github.com/advisories/GHSA-gmph-wf7j-9gcm
Type: github-advisory

## Affected
- Go: `go.etcd.io/etcd/v3` — affected 3.4.10

## Details
Authentication vulnerability found in Etcd-io v.3.4.10 allows remote attackers to escalate privileges via the debug function.

This has been fixed in v.[3.5.8](https://github.com/etcd-io/etcd/blob/main/CHANGELOG/CHANGELOG-3.5.md#etcd-server) and was also backported to [3.4](https://github.com/etcd-io/etcd/pull/15655) and [3.5](https://github.com/etcd-io/etcd/pull/15653).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28235
- https://github.com/etcd-io/etcd/pull/15648
- https://github.com/etcd-io/etcd
- https://github.com/lucyxss/etcd-3.4.10-test/blob/master/temp4cj.png
- https://github.com/lucyxss/etcd-3.4.10-test/blob/master/temp4cj_2.png
- http://etcd.com
