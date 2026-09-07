# [M] Cross site scripting in the system log

## Summary
Severity: Medium
Advisory: GHSA-h58v-c6rf-g9f7
CVE: CVE-2021-35210
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-h58v-c6rf-g9f7
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.9.16
- Packagist: `contao/core-bundle` — affected >=4.10.0 <4.11.5
- Packagist: `contao/contao` — affected >=4.5.0 <4.9.16
- Packagist: `contao/contao` — affected >=4.10.0 <4.11.5

## Details
### Impact

It is possible to inject code into the `tl_log` table that will be executed in the browser when the system log is called in the back end.

### Patches

Update to Contao 4.9.16 or 4.11.5.

### Workarounds

Disable the system log module in the back end for all users (especially admin users).

### References

https://contao.org/en/security-advisories/cross-site-scripting-in-the-system-log-2021

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-h58v-c6rf-g9f7
- https://nvd.nist.gov/vuln/detail/CVE-2021-35210
- https://contao.org/en/security-advisories/cross-site-scripting-in-the-system-log-2021.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2021-35210.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2021-35210.yaml
- https://github.com/contao/contao
