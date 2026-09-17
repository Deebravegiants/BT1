# [H] openssl-src's infinite loop in `BN_mod_sqrt()` reachable when parsing certificates

## Summary
Severity: High
Advisory: GHSA-x3mh-jvjw-3xwx
CVE: CVE-2022-0778
CWE: CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-x3mh-jvjw-3xwx
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.5
- crates.io: `openssl-src` — affected >=0 <111.18.0

## Details
The BN_mod_sqrt() function, which computes a modular square root, contains a bug that can cause it to loop forever for non-prime moduli. Internally this function is used when parsing certificates that contain elliptic curve public keys in compressed form or explicit elliptic curve parameters with a base point encoded in compressed form. It is possible to trigger the infinite loop by crafting a certificate that has invalid explicit curve parameters. Since certificate parsing happens prior to verification of the certificate signature, any process that parses an externally supplied certificate may thus be subject to a denial of service attack. The infinite loop can also be reached when parsing crafted private keys as they can contain explicit elliptic curve parameters. Thus vulnerable situations include: - TLS clients consuming server certificates - TLS servers consuming client certificates - Hosting providers taking certificates or private keys from customers - Certificate authorities parsing certification requests from subscribers - Anything else which parses ASN.1 elliptic curve parameters Also any other applications that use the BN_mod_sqrt() where the attacker can control the parameter values are vulnerable to this DoS issue. In the OpenSSL 1.0.2 version the public key is not parsed during initial parsing of the certificate which makes it slightly harder to trigger the infinite loop. However any operation which requires the public key from the certificate will trigger the infinite loop. In particular the attacker can use a self-signed certificate to trigger the loop during verification of the certificate signature. This issue affects OpenSSL versions 1.0.2, 1.1.1 and 3.0. It was addressed in the releases of 1.1.1n and 3.0.2 on the 15th March 2022. Fixed in OpenSSL 3.0.2 (Affected 3.0.0,3.0.1). Fixed in OpenSSL 1.1.1n (Affected 1.1.1-1.1.1m). Fixed in OpenSSL 1.0.2zd (Affected 1.0.2-1.0.2zc).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0778
- https://rustsec.org/advisories/RUSTSEC-2022-0014.html
- https://security.gentoo.org/glsa/202210-02
- https://security.netapp.com/advisory/ntap-20220321-0002
- https://security.netapp.com/advisory/ntap-20220429-0005
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://support.apple.com/kb/HT213255
- https://support.apple.com/kb/HT213256
- https://support.apple.com/kb/HT213257
- https://www.debian.org/security/2022/dsa-5103
- https://www.openssl.org/news/secadv/20220315.txt
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.tenable.com/security/tns-2022-06
- https://www.tenable.com/security/tns-2022-07
- https://www.tenable.com/security/tns-2022-08
- https://www.tenable.com/security/tns-2022-09
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0002
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W6K3PR542DXWLEFFMFIDMME4CWMHJRMG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GDB3GQVJPXJE7X5C5JN6JAA4XUDWD6E6
