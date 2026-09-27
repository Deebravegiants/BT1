# [C] FreeRDP OutOfBound Read in zgfx_decompress_segment

## Summary
Severity: Critical
Advisory: CVE-2024-32041
Aliases: GHSA-5r4p-mfx2-m44r
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-22
Source: https://osv.dev/vulnerability/CVE-2024-32041
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. FreeRDP based clients that use a version of FreeRDP prior to 3.5.0 or 2.11.6 are vulnerable to out-of-bounds read. Versions 3.5.0 and 2.11.6 patch the issue. As a workaround, deactivate `/gfx` (on by default, set `/bpp` or `/rfx` options instead.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/2.11.6
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.5.0
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5JL476WVJSIE7SBUKVJRVA6A52V2HOLZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7SIS6NUNLUBOV4CPCSWKDE6T6C2W3WTR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PX3U6YPZQ7PEJBVKSBUOLWVH7DHROHY5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZKI4UISUXYNBPN4K6TIQKDRTIJ6CDCKJ/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32041.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-5r4p-mfx2-m44r
- https://nvd.nist.gov/vuln/detail/CVE-2024-32041
- https://github.com/FreeRDP/FreeRDP/pull/10077
