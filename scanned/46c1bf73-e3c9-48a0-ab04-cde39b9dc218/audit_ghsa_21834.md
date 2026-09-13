# [H] Unrestricted Upload of File with Dangerous Type in MODX Revolution

## Summary
Severity: High
Advisory: GHSA-j8jp-9x42-4pj5
CVE: CVE-2022-26149
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-27
Source: https://github.com/advisories/GHSA-j8jp-9x42-4pj5
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0

## Details
MODX Revolution through 2.8.3-pl allows remote authenticated administrators to execute arbitrary code by uploading an executable file, because the Uploadable File Types setting can be changed by an administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26149
- https://github.com/modxcms/revolution
- https://github.com/sartlabs/0days/blob/main/Modx/Exploit.txt
- http://packetstormsecurity.com/files/171488/MODX-Revolution-2.8.3-pl-Remote-Code-Execution.html
