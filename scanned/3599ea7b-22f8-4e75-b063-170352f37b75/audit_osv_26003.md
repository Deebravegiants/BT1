# [H] Buffer overflow vulnerabilities in tinydir

## Summary
Severity: High
Advisory: CVE-2023-49287
Aliases: GHSA-jf5r-wgf4-qhxf
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-12-04
Source: https://osv.dev/vulnerability/CVE-2023-49287
Type: osv

## Details
TinyDir is a lightweight C directory and file reader. Buffer overflows in the `tinydir_file_open()` function. This vulnerability has been patched in version 1.2.6.

## References
- http://packetstormsecurity.com/files/176060/TinyDir-1.2.5-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2023/Dec/14
- http://www.openwall.com/lists/oss-security/2023/12/04/1
- https://github.com/cxong/tinydir/releases/tag/1.2.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49287.json
- https://github.com/cxong/tinydir/security/advisories/GHSA-jf5r-wgf4-qhxf
- https://nvd.nist.gov/vuln/detail/CVE-2023-49287
