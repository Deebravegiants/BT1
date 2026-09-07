# [M] openssl-src NULL pointer Dereference in signature_algorithms processing

## Summary
Severity: Medium
Advisory: GHSA-83mx-573x-5rw9
CVE: CVE-2021-3449
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-83mx-573x-5rw9
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=0 <111.15.0

## Details
An OpenSSL TLS server may crash if sent a maliciously crafted renegotiation ClientHello message from a client. If a TLSv1.2 renegotiation ClientHello omits the signature_algorithms extension (where it was present in the initial ClientHello), but includes a signature_algorithms_cert extension then a NULL pointer dereference will result, leading to a crash and a denial of service attack. A server is only vulnerable if it has TLSv1.2 and renegotiation enabled (which is the default configuration). OpenSSL TLS clients are not impacted by this issue. All OpenSSL 1.1.1 versions are affected by this issue. Users of these versions should upgrade to OpenSSL 1.1.1k. OpenSSL 1.0.2 is not impacted by this issue. Fixed in OpenSSL 1.1.1k (Affected 1.1.1-1.1.1j).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3449
- https://www.tenable.com/security/tns-2021-10
- https://www.tenable.com/security/tns-2021-09
- https://www.tenable.com/security/tns-2021-06
- https://www.tenable.com/security/tns-2021-05
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.openssl.org/news/secadv/20210325.txt
- https://www.debian.org/security/2021/dsa-4875
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-openssl-2021-GHY28dJd
- https://security.netapp.com/advisory/ntap-20210513-0002
- https://security.netapp.com/advisory/ntap-20210326-0006
- https://security.gentoo.org/glsa/202103-03
- https://security.FreeBSD.org/advisories/FreeBSD-SA-21:07.openssl.asc
- https://rustsec.org/advisories/RUSTSEC-2021-0055.html
- https://rustsec.org/advisories/RUSTSEC-2021-0055
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2021-0013
