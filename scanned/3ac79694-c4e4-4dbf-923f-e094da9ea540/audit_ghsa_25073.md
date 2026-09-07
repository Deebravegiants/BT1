# [M] Rancher Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6m8r-jh89-rq7h
CVE: CVE-2021-25313
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6m8r-jh89-rq7h
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.6
- Go: `github.com/rancher/rancher` — affected >=2.4.0 <2.4.14
- Go: `github.com/rancher/rancher` — affected >=0 <2.3.11

## Details
A Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Rancher allows remote attackers to execute JavaScript via malicious links. This issue affects: SUSE Rancher Rancher versions prior to 2.5.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25313
- https://github.com/rancher/rancher/issues/31583
- https://bugzilla.suse.com/show_bug.cgi?id=1181852
- https://github.com/rancher/rancher/releases/tag/v2.3.11
- https://github.com/rancher/rancher/releases/tag/v2.4.14
- https://github.com/rancher/rancher/releases/tag/v2.5.6
