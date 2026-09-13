# [M] Information disclosure in the Contao backend

## Summary
Severity: Medium
Advisory: GHSA-4mvc-qc5w-v5qr
CVE: CVE-2019-19712
CWE: CWE-276
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-12-17
Source: https://github.com/advisories/GHSA-4mvc-qc5w-v5qr
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.46
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.8.6
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.46
- Packagist: `contao/contao` — affected >=4.5.0 <4.8.6

## Details
### Impact

Back end users can manipulate the details view URL to show pages and articles that have not been enabled for them.

### Patches

Update to Contao 4.4.46 or 4.8.6.

### Workarounds

None.

### References

https://contao.org/en/security-advisories/information-disclosure-in-the-back-end

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-4mvc-qc5w-v5qr
- https://nvd.nist.gov/vuln/detail/CVE-2019-19712
- https://contao.org/en/news.html
- https://contao.org/en/security-advisories/information-disclosure-in-the-back-end.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2019-19712.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2019-19712.yaml
- https://github.com/contao/contao
