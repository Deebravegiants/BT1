# [H] CVE-2016-5684

## Summary
Severity: High
Advisory: CVE-2016-5684
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-5684
Type: osv

## Details
An exploitable out-of-bounds write vulnerability exists in the XMP image handling functionality of the FreeImage library. A specially crafted XMP file can cause an arbitrary memory overwrite resulting in code execution. An attacker can provide a malicious image to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/93287
- https://usn.ubuntu.com/3925-1/
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- http://www.talosintelligence.com/reports/TALOS-2016-0189/
- https://security.gentoo.org/glsa/201701-68
