# [M] Mojo::JWT versions before 1.02 for Perl verify HMAC signatures with a non-constant-time string comparison

## Summary
Severity: Medium
Advisory: CVE-2026-9537
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-9537
Type: osv

## Details
Mojo::JWT versions before 1.02 for Perl verify HMAC signatures with a non-constant-time string comparison.

The decode() method compares the supplied signature to the recomputed HMAC with Perl's eq operator, which stops at the first differing byte, so the comparison time varies with the number of matching leading bytes.

A caller that decodes attacker supplied tokens leaks the expected signature through this timing variation, which can be aggregated over many requests to recover the signature and forge a token.

## References
- http://www.openwall.com/lists/oss-security/2026/07/17/11
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9537.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9537
- https://github.com/jberger/Mojo-JWT/commit/b8aefb846613e44b5b12bc170898ffd5b05094a2.patch
- http://github.com/jberger/Mojo-JWT
