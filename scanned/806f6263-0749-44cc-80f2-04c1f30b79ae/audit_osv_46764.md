# [H] CVE-2015-1789

## Summary
Severity: High
Advisory: CVE-2015-1789
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-06-12
Source: https://osv.dev/vulnerability/CVE-2015-1789
Type: osv

## Details
The X509_cmp_time function in crypto/x509/x509_vfy.c in OpenSSL before 0.9.8zg, 1.0.0 before 1.0.0s, 1.0.1 before 1.0.1n, and 1.0.2 before 1.0.2b allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted length field in ASN1_TIME data, as demonstrated by an attack against a server that supports client authentication with a custom verification callback.

## References
- http://fortiguard.com/advisory/openssl-vulnerabilities-june-2015
- http://ftp.netbsd.org/pub/NetBSD/security/advisories/NetBSD-SA2015-008.txt.asc
- http://rhn.redhat.com/errata/RHSA-2015-1115.html
- http://rhn.redhat.com/errata/RHSA-2015-1197.html
- http://www.debian.org/security/2015/dsa-3287
- http://www.fortiguard.com/advisory/2015-06-11-fortinet-vulnerability-openssl-vulnerabilities-june-2015
- http://www.fortiguard.com/advisory/openssl-vulnerabilities-june-2015
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2016-2881720.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2017-3236622.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.ubuntu.com/usn/USN-2639-1
- https://bto.bluecoat.com/security-advisory/sa98
- https://security.gentoo.org/glsa/201506-02
- https://www.arista.com/en/support/advisories-notices/security-advisories/1144-security-advisory-11
- https://www.openssl.org/news/secadv_20150611.txt
- https://github.com/openssl/openssl/commit/f48b83b4fb7d6689584cf25f61ca63a4891f5b11
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10694
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10733
