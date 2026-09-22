# [M] Contao affected by directory traversal in the file selector widget

## Summary
Severity: Medium
Advisory: GHSA-4p75-5p53-65m9
CVE: CVE-2024-45604
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-4p75-5p53-65m9
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=0 <4.13.49

## Details
### Impact

Back end users can list files outside their file mounts or the document root in the FileSelector widget.

### Patches

Update to Contao 4.13.49.

### Workarounds

None.

### References

https://contao.org/en/security-advisories/directory-traversal-in-the-fileselector-widget

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

### Credits

Thanks to Jakob Steeg from usd AG for reporting this vulnerability.

## References
- https://github.com/contao/contao/security/advisories/GHSA-4p75-5p53-65m9
- https://nvd.nist.gov/vuln/detail/CVE-2024-45604
- https://github.com/contao/contao/commit/63409c6bdfd95197d9906e229d765b630d45742e
- https://contao.org/en/security-advisories/directory-traversal-in-the-fileselector-widget
- https://github.com/contao/contao
