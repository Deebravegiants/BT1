# [H] Undertow incorrectly parses cookies

## Summary
Severity: High
Advisory: GHSA-3jrv-jgp8-45v3
CVE: CVE-2023-4639
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-17
Source: https://github.com/advisories/GHSA-3jrv-jgp8-45v3
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.11.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.30.Final

## Details
A flaw was found in Undertow, which incorrectly parses cookies with certain value-delimiting characters in incoming requests. This issue could allow an attacker to construct a cookie value to exfiltrate HttpOnly cookie values or spoof arbitrary additional cookie values, leading to unauthorized data access or modification. The main threat from this flaw impacts data confidentiality and integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4639
- https://github.com/undertow-io/undertow/commit/1f93a979d2ac264798e5779b5b7172dfafe0066f
- https://access.redhat.com/errata/RHSA-2024:1674
- https://access.redhat.com/errata/RHSA-2024:1675
- https://access.redhat.com/errata/RHSA-2024:1676
- https://access.redhat.com/errata/RHSA-2024:1677
- https://access.redhat.com/errata/RHSA-2024:2763
- https://access.redhat.com/errata/RHSA-2024:2764
- https://access.redhat.com/errata/RHSA-2024:3919
- https://access.redhat.com/security/cve/CVE-2023-4639
- https://bugzilla.redhat.com/show_bug.cgi?id=2166022
- https://github.com/undertow-io/undertow
- https://security.netapp.com/advisory/ntap-20250207-0001
