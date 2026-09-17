# [M] Cobbler Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-4vc9-4xpq-77vm
CVE: CVE-2016-9605
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4vc9-4xpq-77vm
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0

## Details
A flaw was found in cobbler software component version 2.6.11-1. It suffers from an invalid parameter validation vulnerability, leading the arbitrary file reading. The flaw is triggered by navigating to a vulnerable URL via cobbler-web on a default installation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9605
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9605
- https://github.com/cobbler/cobbler
