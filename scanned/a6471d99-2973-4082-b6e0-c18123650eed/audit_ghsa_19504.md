# [M] Silverstripe cross-site scripting (XSS) attack in elemental "Content blocks in use" report

## Summary
Severity: Medium
Advisory: GHSA-x8xm-c7p8-2pj2
CVE: CVE-2025-25197
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-x8xm-c7p8-2pj2
Type: github-advisory

## Affected
- Packagist: `dnadesign/silverstripe-elemental` — affected >=2.1.2 <5.3.12

## Details
An elemental block can include an XSS payload, which can be executed when viewing the "Content blocks in use" report.

The vulnerability is specific to that report and is a result of failure to cast input prior to including it in the grid field.

### References

- https://www.silverstripe.org/download/security-releases/CVE-2025-25197

## References
- https://github.com/silverstripe/silverstripe-elemental/security/advisories/GHSA-x8xm-c7p8-2pj2
- https://nvd.nist.gov/vuln/detail/CVE-2025-25197
- https://github.com/silverstripe/silverstripe-elemental/pull/1345
- https://github.com/silverstripe/silverstripe-elemental/commit/34ff4ed498ccab94cc5f55ef9a56c37f491eda1d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dnadesign/silverstripe-elemental/CVE-2025-25197.yaml
- https://github.com/silverstripe/silverstripe-elemental
- https://www.silverstripe.org/download/security-releases/cve-2025-25197
