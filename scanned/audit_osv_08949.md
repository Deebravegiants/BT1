# [H] CVE-2016-7054

## Summary
Severity: High
Advisory: CVE-2016-7054
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/CVE-2016-7054
Type: osv

## Details
In OpenSSL 1.1.0 before 1.1.0c, TLS connections using *-CHACHA20-POLY1305 ciphersuites are susceptible to a DoS attack by corrupting larger payloads. This can result in an OpenSSL crash. This issue is not considered to be exploitable beyond a DoS.

## References
- http://www.securitytracker.com/id/1037261
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03744en_us
- https://www.exploit-db.com/exploits/40899/
- http://www.securityfocus.com/bid/94238
- https://www.openssl.org/news/secadv/20161110.txt
