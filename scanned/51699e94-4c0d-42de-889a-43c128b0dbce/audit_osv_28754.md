# [C] Multiple Broken Function-Level Authorization vulnerabilities in casgate

## Summary
Severity: Critical
Advisory: CVE-2024-36108
Aliases: GHSA-mj5q-rc67-h56c
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-31
Source: https://osv.dev/vulnerability/CVE-2024-36108
Type: osv

## Details
casgate is an Open Source Identity and Access Management system. In affected versions `casgate` allows remote unauthenticated attacker to obtain sensitive information via GET request to an API endpoint. This issue has been addressed in PR #201 which is pending merge. An attacker could use `id` parameter of GET requests with value `anonymous/ anonymous` to bypass authorization on certain API endpoints. Successful exploitation of the vulnerability could lead to account takeover, privilege escalation or provide attacker with credential to other services. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36108.json
- https://github.com/casgate/casgate/security/advisories/GHSA-mj5q-rc67-h56c
- https://nvd.nist.gov/vuln/detail/CVE-2024-36108
- https://github.com/casgate/casgate/pull/201
