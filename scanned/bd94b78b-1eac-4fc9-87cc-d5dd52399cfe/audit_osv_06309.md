# [H] Memory race condition in ssl.SSLContext certificate store methods

## Summary
Severity: High
Advisory: BIT-libpython-2024-0397
Aliases: BIT-python-2024-0397, BIT-python-min-2024-0397, CVE-2024-0397, PSF-2024-4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-0397
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.12.0 <3.12.3

## Details
A defect was discovered in the Python “ssl” module where there is a memory
race condition with the ssl.SSLContext methods “cert_store_stats()” and
“get_ca_certs()”. The race condition can be triggered if the methods are
called at the same time as certificates are loaded into the SSLContext,
such as during the TLS handshake with a certificate directory configured.
This issue is fixed in CPython 3.10.14, 3.11.9, 3.12.3, and 3.13.0.

## References
- http://www.openwall.com/lists/oss-security/2024/06/17/2
- https://github.com/python/cpython/commit/01c37f1d0714f5822d34063ca7180b595abf589d
- https://github.com/python/cpython/commit/29c97287d205bf2f410f4895ebce3f43b5160524
- https://github.com/python/cpython/commit/37324b421b72b7bc9934e27aba85d48d4773002e
- https://github.com/python/cpython/commit/542f3272f56f31ed04e74c40635a913fbc12d286
- https://github.com/python/cpython/commit/b228655c227b2ca298a8ffac44d14ce3d22f6faa
- https://github.com/python/cpython/commit/bce693111bff906ccf9281c22371331aaff766ab
- https://github.com/python/cpython/issues/114572
- https://github.com/python/cpython/pull/114573
- https://mail.python.org/archives/list/security-announce@python.org/thread/BMAK5BCGKYWNJOACVUSLUF6SFGBIM4VP/
- https://nvd.nist.gov/vuln/detail/CVE-2024-0397
- https://security.netapp.com/advisory/ntap-20250411-0006/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
