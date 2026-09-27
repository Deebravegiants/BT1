# [H] Quicly has assertion failures

## Summary
Severity: High
Advisory: CVE-2025-61684
Aliases: GHSA-wr3c-345m-43v9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2025-61684
Type: osv

## Details
Quicly, an IETF QUIC protocol implementation, is susceptible to a denial-of-service attack prior to commit d9d3df6a8530a102b57d840e39b0311ce5c9e14e. A remote attacker can exploit these bugs to trigger an assertion failure that crashes process using Quicly. Commit d9d3df6a8530a102b57d840e39b0311ce5c9e14e fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61684.json
- https://github.com/h2o/quicly/security/advisories/GHSA-wr3c-345m-43v9
- https://nvd.nist.gov/vuln/detail/CVE-2025-61684
- https://github.com/h2o/quicly/commit/d9d3df6a8530a102b57d840e39b0311ce5c9e14e
