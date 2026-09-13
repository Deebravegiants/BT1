# [H] Auth Token can be passed dummy or wrong the middleware response is 200 OK

## Summary
Severity: High
Advisory: CVE-2024-52528
Aliases: GHSA-jqx6-gm7f-vp7m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52528
Type: osv

## Details
Budget Control Gateway acts as an entry point for incoming requests and routes them to the appropriate microservices for Budget Control. Budget Control Gateway does not properly validate auth tokens, which allows attackers to bypass intended restrictions. This vulnerability is fixed in 1.5.2.

## References
- https://github.com/BudgetControl/Gateway/security/advisories/GHSA-jqx6-gm7f-vp7m
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52528.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52528
