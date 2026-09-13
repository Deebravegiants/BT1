# [M] Improper authorization in zenml

## Summary
Severity: Medium
Advisory: GHSA-9x88-4jg8-4vf7
CVE: CVE-2024-2035
CWE: CWE-1220, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-9x88-4jg8-4vf7
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.56.2

## Details
An improper authorization vulnerability exists in the zenml-io/zenml repository, specifically within the API PUT /api/v1/users/id endpoint. This vulnerability allows any authenticated user to modify the information of other users, including changing the `active` status of user accounts to false, effectively deactivating them. This issue affects version 0.55.3 and was fixed in version 0.56.2. The impact of this vulnerability is significant as it allows for the deactivation of admin accounts, potentially disrupting the functionality and security of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2035
- https://github.com/zenml-io/zenml/commit/b95f083efffa56831cd41d8ed536aeb0b6038fa3
- https://github.com/pypa/advisory-database/tree/main/vulns/zenml/PYSEC-2024-169.yaml
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/1cfc6493-082e-4229-9f2f-496801a6557c
