# [H] CVE-2019-5443

## Summary
Severity: High
Advisory: CVE-2019-5443
Aliases: CURL-CVE-2019-5443
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-02
Source: https://osv.dev/vulnerability/CVE-2019-5443
Type: osv

## Details
A non-privileged user or program can put code and a config file in a known non-privileged path (under C:/usr/local/) that will make curl <= 7.65.1 automatically run the code (as an openssl "engine") on invocation. If that curl is invoked by a privileged user it can do anything it wants.

## References
- http://www.securityfocus.com/bid/108881
- https://security.netapp.com/advisory/ntap-20191017-0002/
- http://www.openwall.com/lists/oss-security/2019/06/24/1
- https://curl.haxx.se/docs/CVE-2019-5443.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
