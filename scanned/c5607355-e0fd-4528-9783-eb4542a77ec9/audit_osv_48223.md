# [H] CVE-2017-2887

## Summary
Severity: High
Advisory: CVE-2017-2887
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/CVE-2017-2887
Type: osv

## Details
An exploitable buffer overflow vulnerability exists in the XCF property handling functionality of SDL_image 2.0.1. A specially crafted xcf file can cause a stack-based buffer overflow resulting in potential code execution. An attacker can provide a specially crafted XCF file to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/101215
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0394
- https://www.debian.org/security/2018/dsa-4177
- https://www.debian.org/security/2018/dsa-4184
