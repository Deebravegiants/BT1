# [C] openssl-src heap memory corruption with RSA private key operation

## Summary
Severity: Critical
Advisory: GHSA-735f-pg76-fxc4
CVE: CVE-2022-2274
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-02
Source: https://github.com/advisories/GHSA-735f-pg76-fxc4
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.8 <300.0.9

## Details
The OpenSSL 3.0.4 release introduced a serious bug in the RSA implementation for X86_64 CPUs supporting the AVX512IFMA instructions. This issue makes the RSA implementation with 2048 bit private keys incorrect on such machines and memory corruption will happen during the computation. As a consequence of the memory corruption an attacker may be able to trigger a remote code execution on the machine performing the computation. SSL/TLS servers or other servers using 2048 bit RSA private keys running on machines supporting AVX512IFMA instructions of the X86_64 architecture are affected by this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2274
- https://github.com/openssl/openssl/issues/18625
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=4d8a88c134df634ba610ff8db1eb8478ac5fd345
- https://rustsec.org/advisories/RUSTSEC-2022-0033.html
- https://security.netapp.com/advisory/ntap-20220715-0010
- https://www.openssl.org/news/secadv/20220705.txt
