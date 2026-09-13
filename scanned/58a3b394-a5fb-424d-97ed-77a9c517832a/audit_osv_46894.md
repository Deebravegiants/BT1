# [M] CVE-2015-7744

## Summary
Severity: Medium
Advisory: CVE-2015-7744
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-01-22
Source: https://osv.dev/vulnerability/CVE-2015-7744
Type: osv

## Details
wolfSSL (formerly CyaSSL) before 3.6.8 does not properly handle faults associated with the Chinese Remainder Theorem (CRT) process when allowing ephemeral key exchange without low memory optimizations on a server, which makes it easier for remote attackers to obtain private RSA keys by capturing TLS handshakes, aka a Lenstra attack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00016.html
- http://wolfssl.com/wolfSSL/Docs-wolfssl-changelog.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/cpujan2016-2367955.html
- http://www.securitytracker.com/id/1034708
- https://people.redhat.com/~fweimer/rsa-crt-leaks.pdf
- https://securityblog.redhat.com/2015/09/02/factoring-rsa-keys-with-tls-perfect-forward-secrecy/
- https://wolfssl.com/wolfSSL/Blog/Entries/2015/9/17_Two_Vulnerabilities_Recently_Found%2C_An_Attack_on_RSA_using_CRT_and_DoS_Vulnerability_With_DTLS.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-02/msg00016.html
- https://people.redhat.com/~fweimer/rsa-crt-leaks.pdf
- https://securityblog.redhat.com/2015/09/02/factoring-rsa-keys-with-tls-perfect-forward-secrecy/
- http://www.securitytracker.com/id/1034708
