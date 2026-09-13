# [H] Issue summary: A bug has been identified in the processing of key and initialisation vector (IV)...

## Summary
Severity: High
Advisory: JLSEC-2026-243
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-243
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.0.12+0

## Details
Issue summary: A bug has been identified in the processing of key and
initialisation vector (IV) lengths.  This can lead to potential truncation
or overruns during the initialisation of some symmetric ciphers.

Impact summary: A truncation in the IV can result in non-uniqueness,
which could result in loss of confidentiality for some cipher modes.

When calling `EVP_EncryptInit_ex2()`, `EVP_DecryptInit_ex2()` or
`EVP_CipherInit_ex2()` the provided `OSSL_PARAM` array is processed after
the key and IV have been established.  Any alterations to the key length,
via the "keylen" parameter or the IV length, via the "ivlen" parameter,
within the `OSSL_PARAM` array will not take effect as intended, potentially
causing truncation or overreading of these values.  The following ciphers
and cipher modes are impacted: RC2, RC4, RC5, CCM, GCM and OCB.

For the CCM, GCM and OCB cipher modes, truncation of the IV can result in
loss of confidentiality.  For example, when following NIST's SP 800-38D
section 8.2.1 guidance for constructing a deterministic IV for AES in
GCM mode, truncation of the counter portion could lead to IV reuse.

Both truncations and overruns of the key and overruns of the IV will
produce incorrect results and could, in some cases, trigger a memory
exception.  However, these issues are not currently assessed as security
critical.

Changing the key and/or IV lengths is not considered to be a common operation
and the vulnerable API was recently introduced. Furthermore it is likely that
application developers will have spotted this problem during testing since
decryption would fail unless both peers in the communication were similarly
vulnerable. For these reasons we expect the probability of an application being
vulnerable to this to be quite low. However if an application is vulnerable then
this issue is considered very serious. For these reasons we have assessed this
issue as Moderate severity overall.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this because
the issue lies outside of the FIPS provider boundary.

OpenSSL 3.1 and 3.0 are vulnerable to this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/10/24/1
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-093430.html
- https://cert-portal.siemens.com/productcert/html/ssa-277137.html
- https://cert-portal.siemens.com/productcert/html/ssa-331112.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=0df40630850fb2740e6be6890bb905d3fc623b2d
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=5f69f5c65e483928c4b28ed16af6e5742929f1ee
- https://github.com/advisories/GHSA-xw78-pcr6-wrg8
- https://nvd.nist.gov/vuln/detail/CVE-2023-5363
- https://security.netapp.com/advisory/ntap-20231027-0010
- https://security.netapp.com/advisory/ntap-20231027-0010/
- https://security.netapp.com/advisory/ntap-20240201-0003
- https://security.netapp.com/advisory/ntap-20240201-0003/
- https://security.netapp.com/advisory/ntap-20240201-0004
- https://security.netapp.com/advisory/ntap-20240201-0004/
- https://security.netapp.com/advisory/ntap-20241108-0002
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://www.debian.org/security/2023/dsa-5532
- https://www.openssl.org/news/secadv/20231024.txt
