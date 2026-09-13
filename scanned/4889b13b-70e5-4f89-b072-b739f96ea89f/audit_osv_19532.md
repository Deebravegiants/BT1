# [H] CVE-2021-21843

## Summary
Severity: High
Advisory: CVE-2021-21843
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-18
Source: https://osv.dev/vulnerability/CVE-2021-21843
Type: osv

## Details
Multiple exploitable integer overflow vulnerabilities exist within the MPEG-4 decoding functionality of the GPAC Project on Advanced Content library v1.0.1. A specially crafted MPEG-4 input can cause an integer overflow due to unchecked arithmetic resulting in a heap-based buffer overflow that causes memory corruption. After validating the number of ranges, at [41] the library will multiply the count by the size of the GF_SubsegmentRangeInfo structure. On a 32-bit platform, this multiplication can result in an integer overflow causing the space of the array being allocated to be less than expected. An attacker can convince a user to open a video to trigger this vulnerability.

## References
- https://www.debian.org/security/2021/dsa-4966
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1297
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2021-1297
