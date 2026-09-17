# [C] FreeRDP Integer overflow & OutOfBound Write in clear_decompress_residual_data

## Summary
Severity: Critical
Advisory: CVE-2024-32039
Aliases: GHSA-q5h8-7j42-j4r9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-22
Source: https://osv.dev/vulnerability/CVE-2024-32039
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. FreeRDP based clients using a version of FreeRDP prior to 3.5.0 or 2.11.6 are vulnerable to integer overflow and out-of-bounds write. Versions 3.5.0 and 2.11.6 patch the issue. As a workaround, do not use `/gfx` options (e.g. deactivate with `/bpp:32` or `/rfx` as it is on by default).

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/2.11.6
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.5.0
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5JL476WVJSIE7SBUKVJRVA6A52V2HOLZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7SIS6NUNLUBOV4CPCSWKDE6T6C2W3WTR/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PX3U6YPZQ7PEJBVKSBUOLWVH7DHROHY5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZKI4UISUXYNBPN4K6TIQKDRTIJ6CDCKJ/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32039.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-q5h8-7j42-j4r9
- https://nvd.nist.gov/vuln/detail/CVE-2024-32039
- https://github.com/FreeRDP/FreeRDP/pull/10077
