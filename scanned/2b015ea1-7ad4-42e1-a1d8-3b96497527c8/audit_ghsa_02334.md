# [H] Privilege escalation via form generator

## Summary
Severity: High
Advisory: GHSA-hq5m-mqmx-fw6m
CVE: CVE-2021-37627
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-hq5m-mqmx-fw6m
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.56
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.9.18
- Packagist: `contao/core-bundle` — affected >=4.10.0 <4.11.7
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.56
- Packagist: `contao/contao` — affected >=4.5.0 <4.9.18
- Packagist: `contao/contao` — affected >=4.10.0 <4.11.7

## Details
### Impact

It is possible for untrusted users to gain administrator rights with the form generator.

Installations are only affected if there are untrusted back end users with access to the form generator.

### Patches

Update to Contao 4.4.56, 4.9.18 or 4.11.7.

### Workarounds

Disable the form generator or disable the login for untrusted back end users.

### References

https://contao.org/en/security-advisories/privilege-escalation-with-the-form-generator

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-hq5m-mqmx-fw6m
- https://nvd.nist.gov/vuln/detail/CVE-2021-37627
- https://contao.org/en/security-advisories/privilege-escalation-with-the-form-generator.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2021-37627.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2021-37627.yaml
- https://github.com/contao/contao
