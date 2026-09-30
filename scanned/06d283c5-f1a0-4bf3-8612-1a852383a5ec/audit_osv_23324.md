# [M] CVE-2022-47662

## Summary
Severity: Medium
Advisory: CVE-2022-47662
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-05
Source: https://osv.dev/vulnerability/CVE-2022-47662
Type: osv

## Details
GPAC MP4Box 2.1-DEV-rev649-ga8f438d20 has a segment fault (/stack overflow) due to infinite recursion in Media_GetSample isomedia/media.c:662

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47662.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47662
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/2359
