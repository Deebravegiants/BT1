# [H] CVE-2017-3733

## Summary
Severity: High
Advisory: CVE-2017-3733
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/CVE-2017-3733
Type: osv

## Details
During a renegotiation handshake if the Encrypt-Then-Mac extension is negotiated where it was not in the original handshake (or vice-versa) then this can cause OpenSSL 1.1.0 before 1.1.0e to crash (dependent on ciphersuite). Both clients and servers are affected.

## References
- http://www.securitytracker.com/id/1037846
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.securityfocus.com/bid/96269
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbgn03728en_us
- https://www.openssl.org/news/secadv/20170216.txt
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://github.com/openssl/openssl/commit/4ad93618d26a3ea23d36ad5498ff4f59eff3a4d2
