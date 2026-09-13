# [M] Smidge is vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-9rvm-p3qm-f4vv
CVE: CVE-2025-11842
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-9rvm-p3qm-f4vv
Type: github-advisory

## Affected
- NuGet: `Smidge` — affected >=0 <4.6.0

## Details
A security vulnerability has been detected in Shazwazza Smidge up to 4.5.1. The impacted element is an unknown function of the component Bundle Handler. The manipulation of the argument Version leads to path traversal. Remote exploitation of the attack is possible. Upgrading to version 4.6.0 is sufficient to resolve this issue. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11842
- https://github.com/Shazwazza/Smidge
- https://github.com/Shazwazza/Smidge/releases/tag/v4.6.0
- https://github.com/asust9/smidge-vuln?tab=readme-ov-file
- https://vuldb.com/?id.328776
- https://vuldb.com/?submit.664905
