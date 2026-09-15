# [H] Resource leakage when decoding certificates and keys

## Summary
Severity: High
Advisory: GHSA-g323-fr93-4j3c
CVE: CVE-2022-1473
CWE: CWE-404, CWE-459
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-04
Source: https://github.com/advisories/GHSA-g323-fr93-4j3c
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.6

## Details
The OPENSSL_LH_flush() function, which empties a hash table, contains a bug that breaks reuse of the memory occuppied by the removed hash table entries. This function is used when decoding certificates or keys. If a long lived process periodically decodes certificates or keys its memory usage will expand without bounds and the process might be terminated by the operating system causing a denial of service. Also traversing the empty hash table entries will take increasingly more time. Typically such long lived processes might be TLS clients or TLS servers configured to accept client certificate authentication. The function was added in the OpenSSL 3.0 version thus older releases are not affected by the issue. Fixed in OpenSSL 3.0.3 (Affected 3.0.0,3.0.1,3.0.2).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1473
- https://github.com/github/advisory-database/issues/405
- https://cert-portal.siemens.com/productcert/pdf/ssa-953464.pdf
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=64c85430f95200b6b51fe9475bd5203f7c19daf1
- https://rustsec.org/advisories/RUSTSEC-2022-0025.html
- https://security.gentoo.org/glsa/202210-02
- https://security.netapp.com/advisory/ntap-20220602-0009
- https://www.openssl.org/news/secadv/20220503.txt
