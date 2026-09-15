# [H] CVE-2016-2233

## Summary
Severity: High
Advisory: CVE-2016-2233
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-2233
Type: osv

## Details
Stack-based buffer overflow in the inbound_cap_ls function in common/inbound.c in HexChat 2.10.2 allows remote IRC servers to cause a denial of service (crash) via a large number of options in a CAP LS message.

## References
- http://www.securityfocus.com/bid/95920
- http://packetstormsecurity.com/files/136563/Hexchat-IRC-Client-2.11.0-CAP-LS-Handling-Buffer-Overflow.html
- https://www.exploit-db.com/exploits/39657/
