# [M] Insert tag injection in the Contao login module

## Summary
Severity: Medium
Advisory: GHSA-jc43-qrrp-98f5
CVE: CVE-2019-19714
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2019-12-17
Source: https://github.com/advisories/GHSA-jc43-qrrp-98f5
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.8.4 <4.8.6
- Packagist: `contao/contao` — affected >=4.8.4 <4.8.6

## Details
### Impact

It is possible to inject insert tags into the login module which will be replaced when the page is rendered.

### Patches

Update to Contao 4.8.6.

### Workarounds

None.

### References

https://contao.org/en/security-advisories/insert-tag-injection-in-the-login-module

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-jc43-qrrp-98f5
- https://nvd.nist.gov/vuln/detail/CVE-2019-19714
- https://contao.org/en/security-advisories/insert-tag-injection-in-the-login-module.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2019-19714.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2019-19714.yaml
- https://github.com/contao/contao
