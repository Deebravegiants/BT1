# [M] Path Traversal Vulnerability in apport-unpack

## Summary
Severity: Medium
Advisory: CVE-2026-77113
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77113
Type: osv

## Details
Path traversal in apport-unpack in Canonical Apport before 2.36.0, 2.34.2, and 2.28.4 on Linux allows an attacker to create or overwrite arbitrary files with the privileges of the executing user via an attacker controlled key names in crash report files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77113
- https://launchpad.net/bugs/2161697
- https://github.com/canonical/apport/pull/646
- https://github.com/canonical/apport
