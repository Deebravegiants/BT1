# [H] POLY1305 MAC implementation corrupts XMM registers on Windows

## Summary
Severity: High
Advisory: CVE-2023-4807
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-08
Source: https://osv.dev/vulnerability/CVE-2023-4807
Type: osv

## Details
Issue summary: The POLY1305 MAC (message authentication code) implementation
contains a bug that might corrupt the internal state of applications on the
Windows 64 platform when running on newer X86_64 processors supporting the
AVX512-IFMA instructions.

Impact summary: If in an application that uses the OpenSSL library an attacker
can influence whether the POLY1305 MAC algorithm is used, the application
state might be corrupted with various application dependent consequences.

The POLY1305 MAC (message authentication code) implementation in OpenSSL does
not save the contents of non-volatile XMM registers on Windows 64 platform
when calculating the MAC of data larger than 64 bytes. Before returning to
the caller all the XMM registers are set to zero rather than restoring their
previous content. The vulnerable code is used only on newer x86_64 processors
supporting the AVX512-IFMA instructions.

The consequences of this kind of internal application state corruption can
be various - from no consequences, if the calling application does not
depend on the contents of non-volatile XMM registers at all, to the worst
consequences, where the attacker could get complete control of the application
process. However given the contents of the registers are just zeroized so
the attacker cannot put arbitrary values inside, the most likely consequence,
if any, would be an incorrect result of some application dependent
calculations or a crash leading to a denial of service.

The POLY1305 MAC algorithm is most frequently used as part of the
CHACHA20-POLY1305 AEAD (authenticated encryption with associated data)
algorithm. The most common usage of this AEAD cipher is with TLS protocol
versions 1.2 and 1.3 and a malicious client can influence whether this AEAD
cipher is used by the server. This implies that server applications using
OpenSSL can be potentially impacted. However we are currently not aware of
any concrete application that would be affected by this issue therefore we
consider this a Low severity security issue.

As a workaround the AVX512-IFMA instructions support can be disabled at
runtime by setting the environment variable OPENSSL_ia32cap:

   OPENSSL_ia32cap=:~0x200000

The FIPS provider is not affected by this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4807.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4807
- https://security.netapp.com/advisory/ntap-20230921-0001/
- https://www.openssl.org/news/secadv/20230908.txt
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=4bfac4471f53c4f74c8d81020beb938f92d84ca5
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=6754de4a121ec7f261b16723180df6592cbb4508
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=a632d534c73eeb3e3db8c7540d811194ef7c79ff
