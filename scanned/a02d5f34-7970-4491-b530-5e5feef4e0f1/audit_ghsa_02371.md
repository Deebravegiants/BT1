# [M] Integer Overflow in openssl-src

## Summary
Severity: Medium
Advisory: GHSA-84rm-qf37-fgc2
CVE: CVE-2021-23841
CWE: CWE-190, CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-84rm-qf37-fgc2
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=0 <111.14.0

## Details
Calls to EVP_CipherUpdate, EVP_EncryptUpdate and EVP_DecryptUpdate may overflow the output length argument in some cases where the input length is close to the maximum permissable length for an integer on the platform. In such cases the return value from the function call will be 1 (indicating success), but the output length value will be negative. This could cause applications to behave incorrectly or crash. OpenSSL versions 1.1.1i and below are affected by this issue. Users of these versions should upgrade to OpenSSL 1.1.1j. OpenSSL versions 1.0.2x and below are affected by this issue. However OpenSSL 1.0.2 is out of support and no longer receiving public updates. Premium support customers of OpenSSL 1.0.2 should upgrade to 1.0.2y. Other users should upgrade to 1.1.1j. Fixed in OpenSSL 1.1.1j (Affected 1.1.1-1.1.1i). Fixed in OpenSSL 1.0.2y (Affected 1.0.2-1.0.2x).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23841
- https://www.tenable.com/security/tns-2021-09
- https://www.tenable.com/security/tns-2021-03
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.openssl.org/news/secadv/20210216.txt
- https://www.debian.org/security/2021/dsa-4855
- https://support.apple.com/kb/HT212534
- https://support.apple.com/kb/HT212529
- https://support.apple.com/kb/HT212528
- https://security.netapp.com/advisory/ntap-20210513-0002
- https://security.netapp.com/advisory/ntap-20210219-0009
- https://security.gentoo.org/glsa/202103-03
- https://rustsec.org/advisories/RUSTSEC-2021-0058.html
- https://rustsec.org/advisories/RUSTSEC-2021-0058
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44846
- https://github.com/alexcrichton/openssl-src-rs
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=9b1129239f3ebb1d1c98ce9ed41d5c9476c47cb2
