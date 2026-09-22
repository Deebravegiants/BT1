# [H] openssl-src contains Double free after calling `PEM_read_bio_ex`

## Summary
Severity: High
Advisory: GHSA-v5w6-wcm8-jm4q
CVE: CVE-2022-4450
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-v5w6-wcm8-jm4q
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=0 <111.25.0
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.12

## Details
The function `PEM_read_bio_ex()` reads a PEM file from a BIO and parses and decodes the "name" (e.g. "CERTIFICATE"), any header data and the payload data. If the function succeeds then the "name_out", "header" and "data" arguments are populated with pointers to buffers containing the relevant decoded data. The caller is responsible for freeing those buffers. It is possible to construct a PEM file that results in 0 bytes of payload data. In this case `PEM_read_bio_ex()` will return a failure code but will populate the header argument with a pointer to a buffer that has already been freed. If the caller also frees this buffer then a double free will occur. This will most likely lead to a crash. This could be exploited by an attacker who has the ability to supply malicious PEM files for parsing to achieve a denial of service attack.

The functions `PEM_read_bio()` and `PEM_read()` are simple wrappers around `PEM_read_bio_ex()` and therefore these functions are also directly affected.

These functions are also called indirectly by a number of other OpenSSL functions including `PEM_X509_INFO_read_bio_ex()` and
`SSL_CTX_use_serverinfo_file()` which are also vulnerable. Some OpenSSL internal uses of these functions are not vulnerable because the caller does not free the header argument if `PEM_read_bio_ex()` returns a failure code. These locations include the `PEM_read_bio_TYPE()` functions as well as the decoders introduced in OpenSSL 3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4450
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=63bcf189be73a9cc1264059bed6f57974be74a83
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=bbcf509bd046b34cca19c766bbddc31683d0858b
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2023-0003
- https://rustsec.org/advisories/RUSTSEC-2023-0010.html
- https://security.gentoo.org/glsa/202402-08
- https://www.openssl.org/news/secadv/20230207.txt
