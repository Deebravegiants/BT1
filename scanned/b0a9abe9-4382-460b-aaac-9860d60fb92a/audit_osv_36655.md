# [M] iccDEV has a heap-buffer-overflow in icXmlParseTextString()

## Summary
Severity: Medium
Advisory: CVE-2026-24852
Aliases: GHSA-q8g2-mp32-3j7f
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24852
Type: osv

## Details
iccDEV provides a set of libraries and tools that allow for the interaction, manipulation, and application of ICC color management profiles. Prior to version 2.3.1.2, a heap buffer over-read when the strlen() function attempts to read a non-null-terminated buffer potentially leaking heap memory contents and causing application termination. This vulnerability affects users of the iccDEV library who process ICC color profiles. ICC Profile Injection vulnerabilities arise when user-controllable input is incorporated into ICC profile data or other structured binary blobs in an unsafe manner. Version 2.3.1.2 contains a fix for the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24852.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-q8g2-mp32-3j7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-24852
- https://github.com/InternationalColorConsortium/iccDEV/commit/3092499cd4d0775f4a716b999899f9c26f9bc614
- https://github.com/InternationalColorConsortium/iccDEV/pull/540
