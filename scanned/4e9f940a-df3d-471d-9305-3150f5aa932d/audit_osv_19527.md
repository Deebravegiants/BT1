# [H] CVE-2021-21838

## Summary
Severity: High
Advisory: CVE-2021-21838
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-18
Source: https://osv.dev/vulnerability/CVE-2021-21838
Type: osv

## Details
Multiple exploitable integer overflow vulnerabilities exist within the MPEG-4 decoding functionality of the GPAC Project on Advanced Content library v1.0.1. A specially crafted MPEG-4 input can cause an integer overflow due to unchecked arithmetic resulting in a heap-based buffer overflow that causes memory corruption. An attacker can convince a user to open a video to trigger this vulnerability.

## References
- https://www.debian.org/security/2021/dsa-4966
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1297
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2021-1297
