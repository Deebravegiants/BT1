# [H] CVE-2016-9037

## Summary
Severity: High
Advisory: CVE-2016-9037
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9037
Type: osv

## Details
An exploitable out-of-bounds array access vulnerability exists in the xrow_header_decode function of Tarantool 1.7.2.0-g8e92715. A specially crafted packet can cause the function to access an element outside the bounds of a global array that is used to determine the type of the specified key's value. This can lead to an out of bounds read within the context of the server. An attacker who exploits this vulnerability can cause a denial of service vulnerability on the server.

## References
- http://www.securityfocus.com/bid/95063
- http://www.talosintelligence.com/reports/TALOS-2016-0255/
