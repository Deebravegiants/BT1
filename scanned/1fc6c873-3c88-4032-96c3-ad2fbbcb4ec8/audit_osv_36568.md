# [H] iccDEV has Heap Buffer Overflow in CIccTagNamedColor2::SetSize()

## Summary
Severity: High
Advisory: CVE-2026-24406
Aliases: GHSA-h9h3-45cm-j95f
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-24
Source: https://osv.dev/vulnerability/CVE-2026-24406
Type: osv

## Details
iccDEV provides libraries and tools for interacting with, manipulating, and applying ICC color management profiles. Versions 2.3.1.1 and below have a Heap Buffer Overflow vulnerability in CIccTagNamedColor2::SetSize(). This occurs when user-controllable input is unsafely incorporated into ICC profile data or other structured binary blobs. Successful exploitation may allow an attacker to perform DoS, manipulate data, bypass application logic and Code Execution. This issue has been fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24406.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-h9h3-45cm-j95f
- https://nvd.nist.gov/vuln/detail/CVE-2026-24406
- https://github.com/InternationalColorConsortium/iccDEV/issues/480
- https://github.com/InternationalColorConsortium/iccDEV/commit/90c71cba2c563b1f5dc84197f827540d1baaea67
