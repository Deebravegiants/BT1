# [H] CVE-2021-21861

## Summary
Severity: High
Advisory: CVE-2021-21861
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-16
Source: https://osv.dev/vulnerability/CVE-2021-21861
Type: osv

## Details
An exploitable integer truncation vulnerability exists within the MPEG-4 decoding functionality of the GPAC Project on Advanced Content library v1.0.1. When processing the 'hdlr' FOURCC code, a specially crafted MPEG-4 input can cause an improper memory allocation resulting in a heap-based buffer overflow that causes memory corruption. An attacker can convince a user to open a video to trigger this vulnerability.

## References
- https://www.debian.org/security/2021/dsa-4966
- https://talosintelligence.com/vulnerability_reports/TALOS-2021-1298
