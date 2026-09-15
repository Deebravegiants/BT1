# [M] Skill-scanner Unsecured Network Binding Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ppfx-73j5-fhxc
CVE: CVE-2026-26057
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-ppfx-73j5-fhxc
Type: github-advisory

## Affected
- PyPI: `cisco-ai-skill-scanner` — affected >=0 <1.0.2

## Details
**Description:**
A vulnerability in the API Server of Skill Scanner could allow a unauthenticated, remote attacker to interact with the server API and either trigger a denial of service (DoS) condition or upload arbitrary files.

This vulnerability is due to an erroneous binding to multiple interfaces. An attacker could exploit this vulnerability by sending API requests to a device exposing the affected API Server. A successful exploit could allow the attacker to consume an excessive amount of resources (memory starvation) or to upload files to arbitrary folders on the affected device.

**Conditions:**
This vulnerability affects Skill-scanner 1.0.1 and earlier releases when the API Server is enabled. The API Server is not enabled by default.

**Fixed Software:**
Skill-scanner software releases 1.0.2 and later contained the fix for this vulnerability.

**For more information:**
If you have any questions or comments about this advisory:
- [Open an issue in cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner/issues)
- Email Cisco Open Source Security ([oss-security@cisco.com](mailto:oss-security@cisco.com)) and Cisco PSIRT ([psirt@cisco.com](mailto:psirt@cisco.com))

**Credits:**

- Research: Richard Tweed (@RichardoC)
- Fix ideation and implementation: Richard Tweed (@RichardoC)
- Release engineering: Vineeth Sai Narajala (@vineethsai7)

## References
- https://github.com/cisco-ai-defense/skill-scanner/security/advisories/GHSA-ppfx-73j5-fhxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-26057
- https://github.com/cisco-ai-defense/skill-scanner/commit/1e35e57f3051ecc89ba845ae7206321c8eac20a1
- https://github.com/cisco-ai-defense/skill-scanner
