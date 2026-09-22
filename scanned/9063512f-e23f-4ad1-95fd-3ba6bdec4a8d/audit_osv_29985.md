# [M] CVE-2024-48463

## Summary
Severity: Medium
Advisory: CVE-2024-48463
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-11-04
Source: https://osv.dev/vulnerability/CVE-2024-48463
Type: osv

## Details
Bruno before 1.29.1 uses Electron shell.openExternal without validation (of http or https) for opening windows within the Markdown docs viewer.

## References
- http://seclists.org/fulldisclosure/2025/Jan/6
- https://gist.github.com/opcod3r/ab69f36d52367df7ffac32a597dff31c
- https://github.com/usebruno/bruno/releases/tag/v1.29.1
- https://www.usebruno.com/changelog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48463.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48463
- https://github.com/usebruno/bruno/pull/3122
