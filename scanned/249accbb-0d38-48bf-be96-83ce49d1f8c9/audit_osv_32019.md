# [M] CVE-2025-22376

## Summary
Severity: Medium
Advisory: CVE-2025-22376
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2025-22376
Type: osv

## Details
In Net::OAuth::Client in the Net::OAuth package before 0.29 for Perl, the default nonce is a 32-bit integer generated from the built-in rand() function, which is not cryptographically strong.

## References
- https://datatracker.ietf.org/doc/html/rfc5849#section-3.3
- https://datatracker.ietf.org/doc/html/rfc5849#section-4.10
- https://metacpan.org/release/KGRENNAN/Net-OAuth-0.28/source/lib/Net/OAuth/Client.pm#L260
- https://metacpan.org/release/RRWO/Net-OAuth-0.29/changes
- https://metacpan.org/release/RRWO/Net-OAuth-0.29/diff/KGRENNAN/Net-OAuth-0.28#lib/Net/OAuth/Client.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22376.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22376
- https://github.com/keeth/Net-OAuth/commit/2aa25e04aadab247ae4063363fcee177161e1f42
- https://www.vulnarium.com/blogpost-2025-01-05
