# [H] CVE-2017-2888

## Summary
Severity: High
Advisory: CVE-2017-2888
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/CVE-2017-2888
Type: osv

## Details
An exploitable integer overflow vulnerability exists when creating a new RGB Surface in SDL 2.0.5. A specially crafted file can cause an integer overflow resulting in too little memory being allocated which can lead to a buffer overflow and potential code execution. An attacker can provide a specially crafted image file to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/101215
- https://lists.debian.org/debian-lts-announce/2021/10/msg00031.html
- https://usn.ubuntu.com/4143-1/
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0395
