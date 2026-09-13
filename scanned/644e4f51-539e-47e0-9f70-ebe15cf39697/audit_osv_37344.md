# [C] CVE-2026-31309

## Summary
Severity: Critical
Advisory: CVE-2026-31309
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-31309
Type: osv

## Details
Improper authorization in the /tequilapi/config/user endpoint of Mysterium Node from v1.21.1-rc0 before v1.36.0 allows an unauthenticated attacker to arbitrarily overwrite the node's configuration and achieve a full node takeover via a crafted POST request.

## References
- https://github.com/mysteriumnetwork/node/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31309.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31309
- https://github.com/mysteriumnetwork/node/commit/bc099fcaff59fee9c8a8f8e07ffff5b3c5df2bb9
- https://github.com/sch8ill/CVE-2026-31309
