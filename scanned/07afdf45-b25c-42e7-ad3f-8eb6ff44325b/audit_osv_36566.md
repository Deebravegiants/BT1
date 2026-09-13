# [H] iccDEV has Null Pointer Deference and Undefined Behavior in CIccXmlArrayType()

## Summary
Severity: High
Advisory: CVE-2026-24404
Aliases: GHSA-hqfg-45jp-hp9f
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-01-24
Source: https://osv.dev/vulnerability/CVE-2026-24404
Type: osv

## Details
iccDEV provides libraries and tools for interacting with, manipulating, and applying ICC color management profiles. In versions 2.3.1.1 and below, CIccXmlArrayType() contains a Null Pointer Dereference and Undefined Behavior vulnerability. This occurs when user-controllable input is unsafely incorporated into ICC profile data or other structured binary blobs. Successful exploitation may allow an attacker to perform DoS, manipulate data, bypass application logic and Code Execution. This issue has been fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24404.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-hqfg-45jp-hp9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-24404
- https://github.com/InternationalColorConsortium/iccDEV/issues/488
- https://github.com/InternationalColorConsortium/iccDEV/commit/cd637eb33f0c8055fa54d8776e00555d3d39ef0c
