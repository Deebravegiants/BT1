# [H] CVE-2025-69516

## Summary
Severity: High
Advisory: CVE-2025-69516
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2025-69516
Type: osv

## Details
A Server-Side Template Injection (SSTI) vulnerability in the /reporting/templates/preview/ endpoint of Amidaware Tactical RMM, affecting versions equal to or earlier than v1.3.1, allows low-privileged users with Report Viewer or Report Manager permissions to achieve remote command execution on the server. This occurs due to improper sanitization of the template_md parameter, enabling direct injection of Jinja2 templates. This occurs due to misuse of the generate_html() function, the user-controlled value is inserted into `env.from_string`, a function that processes Jinja2 templates arbitrarily, making an SSTI possible.

## References
- https://gist.github.com/NtGabrielGomes/7c424367cc316fd7527f668ff076fece
- https://www.amidaware.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69516.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69516
- https://github.com/amidaware/tacticalrmm
