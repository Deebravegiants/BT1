# [H] Taguette password reset link poisoning

## Summary
Severity: High
Advisory: GHSA-7rc8-5c8q-jr6j
CVE: CVE-2025-62527
CWE: CWE-15
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-10-20
Source: https://github.com/advisories/GHSA-7rc8-5c8q-jr6j
Type: github-advisory

## Affected
- PyPI: `taguette` — affected >=0 <1.5.0

## Details
### Impact
An issue has been discovered in Taguette versions prior to 1.5.0. It was possible for an attacker to request password reset email containing a malicious link, allowing the attacker to set the email if clicked by the victim.

### Patches
Users should upgrade to Taguette 1.5.0.

### References
- https://gitlab.com/remram44/taguette/-/issues/331

## References
- https://github.com/remram44/taguette/security/advisories/GHSA-7rc8-5c8q-jr6j
- https://nvd.nist.gov/vuln/detail/CVE-2025-62527
- https://github.com/pypa/advisory-database/tree/main/vulns/taguette/PYSEC-2025-187.yaml
- https://github.com/remram44/taguette
- https://gitlab.com/remram44/taguette/-/issues/331
