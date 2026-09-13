# [H] CVE-2004-1002

## Summary
Severity: High
Advisory: CVE-2004-1002
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2005-03-01
Source: https://osv.dev/vulnerability/CVE-2004-1002
Type: osv

## Details
Integer underflow in pppd in cbcp.c for ppp 2.4.1 allows remote attackers to cause a denial of service (daemon crash) via a CBCP packet with an invalid length value that causes pppd to access an incorrect memory location.

## References
- http://www.securityfocus.com/archive/1/379450
- https://exchange.xforce.ibmcloud.com/vulnerabilities/17874
- https://www.ubuntu.com/usn/usn-12-1/
- http://www.securityfocus.com/archive/1/379450
