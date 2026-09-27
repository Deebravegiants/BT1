# [H] Database password exposed in logs in hoppscotch

## Summary
Severity: High
Advisory: CVE-2023-34097
Aliases: GHSA-qpx8-wq6q-r833
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-05
Source: https://osv.dev/vulnerability/CVE-2023-34097
Type: osv

## Details
hoppscotch is an open source API development ecosystem. In versions prior to 2023.4.5 the database password is exposed in the logs when showing the database connection string. Attackers with access to read system logs will be able to elevate privilege with full access to the database. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34097.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-qpx8-wq6q-r833
- https://nvd.nist.gov/vuln/detail/CVE-2023-34097
- https://github.com/hoppscotch/hoppscotch/commit/15424903ede20b155d764abf4c4f7c2c84c11247
