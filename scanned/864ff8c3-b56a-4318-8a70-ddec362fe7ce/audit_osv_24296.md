# [H] X.400 address type confusion in X.509 GeneralName

## Summary
Severity: High
Advisory: CVE-2023-0286
Aliases: GHSA-x4qr-2fvf-3mr5, PYSEC-2026-800, RUSTSEC-2023-0006
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/CVE-2023-0286
Type: osv

## Details
There is a type confusion vulnerability relating to X.400 address processing
inside an X.509 GeneralName. X.400 addresses were parsed as an ASN1_STRING but
the public structure definition for GENERAL_NAME incorrectly specified the type
of the x400Address field as ASN1_TYPE. This field is subsequently interpreted by
the OpenSSL function GENERAL_NAME_cmp as an ASN1_TYPE rather than an
ASN1_STRING.

When CRL checking is enabled (i.e. the application sets the
X509_V_FLAG_CRL_CHECK flag), this vulnerability may allow an attacker to pass
arbitrary pointers to a memcmp call, enabling them to read memory contents or
enact a denial of service. In most cases, the attack requires the attacker to
provide both the certificate chain and CRL, neither of which need to have a
valid signature. If the attacker only controls one of these inputs, the other
input must already contain an X.400 address as a CRL distribution point, which
is uncommon. As such, this vulnerability is most likely to only affect
applications which have implemented their own functionality for retrieving CRLs
over a network.

## References
- https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-3.6.2-relnotes.txt
- https://ftp.openbsd.org/pub/OpenBSD/patches/7.2/common/018_x509.patch.sig
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2023-0003
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0286.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0286
- https://security.gentoo.org/glsa/202402-08
- https://www.openssl.org/news/secadv/20230207.txt
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=2c6c9d439b484e1ba9830d8454a34fa4f80fdfe9
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=2f7530077e0ef79d98718138716bc51ca0cad658
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=fd2af07dc083a350c959147097003a14a5e8ac4d
