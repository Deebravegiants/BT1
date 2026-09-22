# [H] CVE-2015-8702

## Summary
Severity: High
Advisory: CVE-2015-8702
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2015-8702
Type: osv

## Details
The DNS::GetResult function in dns.cpp in InspIRCd before 2.0.19 allows remote DNS servers to cause a denial of service (netsplit) via an invalid character in a PTR response, as demonstrated by a "\032" (whitespace) character in a hostname.

## References
- http://www.debian.org/security/2016/dsa-3527
- http://www.inspircd.org/2015/04/16/v2019-released.html
- https://security.gentoo.org/glsa/201512-13
- https://github.com/inspircd/inspircd/commit/6058483d9fbc1b904d5ae7cfea47bfcde5c5b559
- https://github.com/inspircd/inspircd/issues/1033
