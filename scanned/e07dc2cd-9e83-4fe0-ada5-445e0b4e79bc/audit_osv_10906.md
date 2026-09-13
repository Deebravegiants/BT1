# [H] CVE-2017-3731

## Summary
Severity: High
Advisory: CVE-2017-3731
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/CVE-2017-3731
Type: osv

## Details
If an SSL/TLS server or client is running on a 32-bit host, and a specific cipher is being used, then a truncated packet can cause that server or client to perform an out-of-bounds read, usually resulting in a crash. For OpenSSL 1.1.0, the crash can be triggered when using CHACHA20/POLY1305; users should upgrade to 1.1.0d. For Openssl 1.0.2, the crash can be triggered when using RC4-MD5; users who have not disabled that algorithm should update to 1.0.2k.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0286.html
- http://www.debian.org/security/2017/dsa-3773
- http://www.securityfocus.com/bid/95813
- http://www.securitytracker.com/id/1037717
- https://access.redhat.com/errata/RHSA-2018:2185
- https://access.redhat.com/errata/RHSA-2018:2186
- https://access.redhat.com/errata/RHSA-2018:2187
- https://github.com/openssl/openssl/commit/00d965474b22b54e4275232bc71ee0c699c5cd21
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:02.openssl.asc
- https://security.gentoo.org/glsa/201702-07
- https://security.netapp.com/advisory/ntap-20171019-0002/
- https://security.paloaltonetworks.com/CVE-2017-3731
- https://source.android.com/security/bulletin/pixel/2017-11-01
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03838en_us
- https://www.openssl.org/news/secadv/20170126.txt
- https://www.tenable.com/security/tns-2017-04
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
