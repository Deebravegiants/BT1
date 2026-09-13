# [H] Create user API role not enforced

## Summary
Severity: High
Advisory: CVE-2024-0795
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2024-0795
Type: osv

## Details
If an attacked was given access to an instance with the admin or manager role there is no backend authentication that would prevent the attacked from creating a new user with an `admin` role and then be able to use this new account to have elevated privileges on the instance

## References
- https://huntr.com/bounties/f69e3307-7b44-4776-ac60-2990990723ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0795.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0795
- https://github.com/mintplex-labs/anything-llm/commit/9a237db3d1f66cdbcf5079599258f5fb251c5564
