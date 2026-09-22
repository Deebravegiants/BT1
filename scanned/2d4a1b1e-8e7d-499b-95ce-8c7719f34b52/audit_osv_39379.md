# [M] Time-based user enumeration in TREK authentication endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-45410
Aliases: GHSA-3552-3c98-x79r
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45410
Type: osv

## Details
TREK is a collaborative travel planner. Prior to 3.0.18, early return on missing user during login flow allowed an attacker to enumerate valid user accounts via response timing discrepancy. When an email address existed in the database, the backend performed a bcrypt password comparison before returning a 401 Unauthorized, adding ~370 ms of latency. When the email did not exist, the backend returned immediately (~10 ms). This ~14× timing difference could be detected without any difference in HTTP status codes or response bodies. This vulnerability is fixed in 3.0.18.

## References
- https://gist.github.com/jubnl/c2402adf85d946c1730867aeecc794de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45410.json
- https://github.com/mauriceboe/TREK/security/advisories/GHSA-3552-3c98-x79r
- https://nvd.nist.gov/vuln/detail/CVE-2026-45410
