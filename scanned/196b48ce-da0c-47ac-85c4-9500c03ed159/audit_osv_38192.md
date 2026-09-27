# [M] Double-free When Checking OCSP Stapled Response

## Summary
Severity: Medium
Advisory: CVE-2026-35188
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-35188
Type: osv

## Details
Issue summary: A malicious server can exploit TLS OCSP stapling by delivering
a crafted response through the status_request extension, triggering a
double-free in the client's certificate verification path.

Impact summary: Successful exploitation allows an attacker to corrupt heap
memory via a double-free, potentially leading to a Denial of Service or
possibly an attacker controlled code execution or other undefined behavior.

If OCSP stapling is enabled and the TLS client connects to a malicious server,
a crafted OCSP stapled response can trigger a double free in the TLS client
when the stapled response is checked.

The OCSP stapling is not enabled by default. Reliable code execution
through a double-free is technically complex and highly environment-dependent
but the Denial of Service impact is straightforward to achieve, warranting
Moderate severity.

No FIPS modules are affected by this issue as the affected code is outside
the OpenSSL FIPS module boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35188.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35188
- https://openssl-library.org/news/secadv/20260609.txt
- https://github.com/openssl/openssl/commit/131145d25659e8749a9ed1afb383484854cffb78
- https://github.com/openssl/openssl/commit/78d0154cffda03aaaac63a087cc523a6b35fa8fd
