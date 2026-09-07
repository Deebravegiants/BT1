# [H] Null pointer deference in openssl-src 

## Summary
Severity: High
Advisory: GHSA-jq65-29v4-4x35
CVE: CVE-2020-1967
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jq65-29v4-4x35
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=111.6.0 <111.9.0

## Details
Server or client applications that call the SSL_check_chain() function during or after a TLS 1.3 handshake may crash due to a NULL pointer dereference as a result of incorrect handling of the "signature_algorithms_cert" TLS extension. The crash occurs if an invalid or unrecognised signature algorithm is received from the peer. This could be exploited by a malicious peer in a Denial of Service attack. OpenSSL version 1.1.1d, 1.1.1e, and 1.1.1f are affected by this issue. This issue did not affect OpenSSL versions prior to 1.1.1d. Fixed in OpenSSL 1.1.1g (Affected 1.1.1d-1.1.1f).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1967
- https://www.tenable.com/security/tns-2021-10
- https://www.tenable.com/security/tns-2020-11
- https://www.tenable.com/security/tns-2020-04
- https://www.tenable.com/security/tns-2020-03
- https://www.synology.com/security/advisory/Synology_SA_20_05_OpenSSL
- https://www.synology.com/security/advisory/Synology_SA_20_05
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.openssl.org/news/secadv/20200421.txt
- https://www.debian.org/security/2020/dsa-4661
- https://security.netapp.com/advisory/ntap-20200717-0004
- https://security.netapp.com/advisory/ntap-20200424-0003
- https://security.gentoo.org/glsa/202004-10
- https://security.FreeBSD.org/advisories/FreeBSD-SA-20:11.openssl.asc
- https://rustsec.org/advisories/RUSTSEC-2020-0015.html
