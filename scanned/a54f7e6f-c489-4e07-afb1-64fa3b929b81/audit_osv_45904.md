# [H] An out of bounds write exists in FreeType versions 2.13.0 and below when attempting to parse font...

## Summary
Severity: High
Advisory: JLSEC-2026-460
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-460
Type: osv

## Affected
- Julia: `FreeType2_jll` — affected >=0 <2.13.1+0

## Details
An out of bounds write exists in FreeType versions 2.13.0 and below (newer versions of FreeType are not vulnerable) when attempting to parse font subglyph structures related to TrueType GX and variable font files. The vulnerable code assigns a signed short value to an unsigned long and then adds a static value causing it to wrap around and allocate too small of a heap buffer. The code then writes up to 6 signed long integers out of bounds relative to this buffer. This may result in arbitrary code execution. This vulnerability may have been exploited in the wild.

## References
- http://www.openwall.com/lists/oss-security/2025/03/13/1
- http://www.openwall.com/lists/oss-security/2025/03/13/11
- http://www.openwall.com/lists/oss-security/2025/03/13/12
- http://www.openwall.com/lists/oss-security/2025/03/13/2
- http://www.openwall.com/lists/oss-security/2025/03/13/3
- http://www.openwall.com/lists/oss-security/2025/03/13/8
- http://www.openwall.com/lists/oss-security/2025/03/14/1
- http://www.openwall.com/lists/oss-security/2025/03/14/2
- http://www.openwall.com/lists/oss-security/2025/03/14/3
- http://www.openwall.com/lists/oss-security/2025/03/14/4
- http://www.openwall.com/lists/oss-security/2025/05/06/3
- http://www.openwall.com/lists/oss-security/2026/04/16/5
- http://www.openwall.com/lists/oss-security/2026/04/19/3
- https://github.com/advisories/GHSA-g8qj-jv5h-78cp
- https://lists.debian.org/debian-lts-announce/2025/03/msg00030.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-27363
- https://source.android.com/docs/security/bulletin/2025-05-01
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-27363
- https://www.facebook.com/security/advisories/cve-2025-27363
