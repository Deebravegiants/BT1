# [H] Certificate check bypass in openssl-src

## Summary
Severity: High
Advisory: GHSA-8hfj-xrj2-pm22
CVE: CVE-2021-3450
CWE: CWE-295
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8hfj-xrj2-pm22
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=111.11.0 <111.15.0

## Details
The X509_V_FLAG_X509_STRICT flag enables additional security checks of the certificates present in a certificate chain. It is not set by default. Starting from OpenSSL version 1.1.1h a check to disallow certificates in the chain that have explicitly encoded elliptic curve parameters was added as an additional strict check. An error in the implementation of this check meant that the result of a previous check to confirm that certificates in the chain are valid CA certificates was overwritten. This effectively bypasses the check that non-CA certificates must not be able to issue other certificates. If a "purpose" has been configured then there is a subsequent opportunity for checks that the certificate is a valid CA. All of the named "purpose" values implemented in libcrypto perform this check. Therefore, where a purpose is set the certificate chain will still be rejected even when the strict flag has been used. A purpose is set by default in libssl client and server certificate verification routines, but it can be overridden or removed by an application. In order to be affected, an application must explicitly set the X509_V_FLAG_X509_STRICT verification flag and either not set a purpose for the certificate verification or, in the case of TLS client or server applications, override the default purpose. OpenSSL versions 1.1.1h and newer are affected by this issue. Users of these versions should upgrade to OpenSSL 1.1.1k. OpenSSL 1.0.2 is not impacted by this issue. Fixed in OpenSSL 1.1.1k (Affected 1.1.1h-1.1.1j).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3450
- https://www.tenable.com/security/tns-2021-09
- https://www.tenable.com/security/tns-2021-08
- https://www.tenable.com/security/tns-2021-05
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.openssl.org/news/secadv/20210325.txt
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-openssl-2021-GHY28dJd
- https://security.netapp.com/advisory/ntap-20210326-0006
- https://security.gentoo.org/glsa/202103-03
- https://security.FreeBSD.org/advisories/FreeBSD-SA-21:07.openssl.asc
- https://rustsec.org/advisories/RUSTSEC-2021-0056.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2021-0013
- https://mta.openssl.org/pipermail/openssl-announce/2021-March/000198.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CCBFLLVQVILIVGZMBJL3IXZGKWQISYNP
- https://kc.mcafee.com/corporate/index?page=content&id=SB10356
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA44845
