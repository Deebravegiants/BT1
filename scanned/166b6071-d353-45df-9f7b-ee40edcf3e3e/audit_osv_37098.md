# [H] NULL Pointer Dereference When Processing a Delta CRL

## Summary
Severity: High
Advisory: CVE-2026-28388
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-28388
Type: osv

## Details
Issue summary: When a delta CRL that contains a Delta CRL Indicator extension
is processed a NULL pointer dereference might happen if the required CRL
Number extension is missing.

Impact summary: A NULL pointer dereference can trigger a crash which
leads to a Denial of Service for an application.

When CRL processing and delta CRL processing is enabled during X.509
certificate verification, the delta CRL processing does not check
whether the CRL Number extension is NULL before dereferencing it.
When a malformed delta CRL file is being processed, this parameter
can be NULL, causing a NULL pointer dereference.

Exploiting this issue requires the X509_V_FLAG_USE_DELTAS flag to be enabled in
the verification context, the certificate being verified to contain a
freshestCRL extension or the base CRL to have the EXFLAG_FRESHEST flag set, and
an attacker to provide a malformed CRL to an application that processes it.

The vulnerability is limited to Denial of Service and cannot be escalated to
achieve code execution or memory disclosure. For that reason the issue was
assessed as Low severity according to our Security Policy.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28388.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28388
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/59c3b3158553ab53275bbbccca5cb305d591cf2e
- https://github.com/openssl/openssl/commit/5a0b4930779cd2408880979db765db919da55139
- https://github.com/openssl/openssl/commit/602542f2c0c2d5edb47128f93eac10b62aeeefb3
- https://github.com/openssl/openssl/commit/a9d187dd1000130100fa7ab915f8513532cb3bb8
- https://github.com/openssl/openssl/commit/d3a901e8d9f021f3e67d6cfbc12e768129862726
