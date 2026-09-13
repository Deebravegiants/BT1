# [H] Potential Use-after-free in DANE Client Code

## Summary
Severity: High
Advisory: CVE-2026-28387
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-28387
Type: osv

## Details
Issue summary: An uncommon configuration of clients performing DANE TLSA-based
server authentication, when paired with uncommon server DANE TLSA records, may
result in a use-after-free and/or double-free on the client side.

Impact summary: A use after free can have a range of potential consequences
such as the corruption of valid data, crashes or execution of arbitrary code.

However, the issue only affects clients that make use of TLSA records with both
the PKIX-TA(0/PKIX-EE(1) certificate usages and the DANE-TA(2) certificate
usage.

By far the most common deployment of DANE is in SMTP MTAs for which RFC7672
recommends that clients treat as 'unusable' any TLSA records that have the PKIX
certificate usages.  These SMTP (or other similar) clients are not vulnerable
to this issue.  Conversely, any clients that support only the PKIX usages, and
ignore the DANE-TA(2) usage are also not vulnerable.

The client would also need to be communicating with a server that publishes a
TLSA RRset with both types of TLSA records.

No FIPS modules are affected by this issue, the problem code is outside the
FIPS module boundary.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28387
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/07e727d304746edb49a98ee8f6ab00256e1f012b
- https://github.com/openssl/openssl/commit/258a8f63b26995ba357f4326da00e19e29c6acbe
- https://github.com/openssl/openssl/commit/444958deaf450aea819171f97ae69eaedede42c3
- https://github.com/openssl/openssl/commit/7a4e08cee62a728d32e60b0de89e6764339df0a7
- https://github.com/openssl/openssl/commit/ec03fa050b3346997ed9c5fef3d0e16ad7db8177
