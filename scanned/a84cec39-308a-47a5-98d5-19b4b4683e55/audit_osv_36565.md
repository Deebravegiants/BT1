# [H] iccDEV Undefined Behavior in CIccProfile::CheckHeader() Leads to Integer Overflow

## Summary
Severity: High
Advisory: CVE-2026-24403
Aliases: GHSA-ph33-qp8j-5q34
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-01-24
Source: https://osv.dev/vulnerability/CVE-2026-24403
Type: osv

## Details
iccDEV provides libraries and tools for interacting with, manipulating, and applying ICC color management profiles. In versions 2.3.1.1 and below, an integer overflow vulnerability exists in icValidateStatus CIccProfile::CheckHeader() when user-controllable input is incorporated into profile data unsafely. Tampering with tag tables, offsets, or size fields can trigger parsing errors, memory corruption, or DoS, potentially enabling arbitrary Code Execution or bypassing application logic. This issue has been fixed in version 2.3.1.2.

## References
- https://github.com/InternationalColorConsortium/iccDEV/commits/d993997005449a0a6958e65b057bd25e17dff89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24403.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-ph33-qp8j-5q34
- https://nvd.nist.gov/vuln/detail/CVE-2026-24403
- https://github.com/InternationalColorConsortium/iccDEV/issues/505
