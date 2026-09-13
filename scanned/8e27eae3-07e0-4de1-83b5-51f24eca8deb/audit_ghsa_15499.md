# [H] Contao affected by remote command execution through file upload

## Summary
Severity: High
Advisory: GHSA-vm6r-j788-hjh5
CVE: CVE-2024-45398
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-vm6r-j788-hjh5
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.13.49
- Packagist: `contao/core-bundle` — affected >=5.0.0 <5.3.15
- Packagist: `contao/core-bundle` — affected >=5.4.0 <5.4.3

## Details
### Impact

Back end users with access to the file manager can upload malicious files and execute them on the server.

### Patches

Update to Contao 4.13.49, 5.3.15 or 5.4.3.

### Workarounds

Configure your web server so it does not execute PHP files and other scripts in the Contao file upload directory.

### References

https://contao.org/en/security-advisories/remote-command-execution-through-file-uploads

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

### Credits

Thanks to Jakob Steeg from usd AG for reporting this vulnerability.

## References
- https://github.com/contao/contao/security/advisories/GHSA-vm6r-j788-hjh5
- https://nvd.nist.gov/vuln/detail/CVE-2024-45398
- https://github.com/contao/contao/commit/9445d509f12a7f1b68a4794dcc5e3e459b363ebb
- https://github.com/contao/contao/commit/a7e39f96ac8fdc281f7caaa96e01deb0e24ac7d3
- https://github.com/contao/contao/commit/f3db59ffe5a6c0e1f705b3230ebd5ff16865280e
- https://contao.org/en/security-advisories/remote-command-execution-through-file-uploads
- https://github.com/contao/contao
