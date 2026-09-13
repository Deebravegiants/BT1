# [H] vantage6 vulnerable to Improper Preservation of Permissions

## Summary
Severity: High
Advisory: GHSA-vvjv-97j8-94xh
CVE: CVE-2023-22738
CWE: CWE-281
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-vvjv-97j8-94xh
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <3.8.0

## Details
### Impact
Assigning existing users to a different organization is currently possible. It may lead to unintended access: if a user from organization A is accidentally assigned to organization B, they will retain their permissions and therefore might be able to access stuff they should not be allowed to access.

### Patches
Update to 3.8.0

### Workarounds
None

### References
None

### For more information
If you have any questions or comments about this advisory:
* Email us at [vantage6@iknl.nl](mailto:vantage6@iknl.nl)

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-vvjv-97j8-94xh
- https://nvd.nist.gov/vuln/detail/CVE-2023-22738
- https://github.com/vantage6/vantage6/commit/798aca1de142a4eca175ef51112e2235642f4f24
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6/PYSEC-2023-53.yaml
- https://github.com/vantage6/vantage6
