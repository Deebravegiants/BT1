# [H] CVE-2018-5410

## Summary
Severity: High
Advisory: CVE-2018-5410
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-07
Source: https://osv.dev/vulnerability/CVE-2018-5410
Type: osv

## Details
Dokan, versions between 1.0.0.5000 and 1.2.0.1000, are vulnerable to a stack-based buffer overflow in the dokan1.sys driver. An attacker can create a device handle to the system driver and send arbitrary input that will trigger the vulnerability. This vulnerability was introduced in the 1.0.0.5000 version update.

## References
- http://www.securityfocus.com/bid/106274
- https://cwe.mitre.org/data/definitions/121.html
- https://kb.cert.org/vuls/id/741315/
- https://github.com/dokan-dev/dokany/releases/tag/v1.2.1.1000
- https://www.exploit-db.com/exploits/46155/
