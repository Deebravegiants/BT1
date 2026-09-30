# [H] Session Fixation

## Summary
Severity: High
Advisory: CVE-2024-25977
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-25977
Type: osv

## Details
The application does not change the session token when using the login or logout functionality. An attacker can set a session token in the victim's browser (e.g. via XSS) and prompt the victim to log in (e.g. via a redirect to the login page). This results in the victim's account being taken over.

## References
- http://seclists.org/fulldisclosure/2024/May/34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25977.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25977
- https://r.sec-consult.com/hawki
- https://github.com/HAWK-Digital-Environments/HAWKI/commit/146967f3148e92d1640ffebc21d8914e2d7fb3f1
- https://github.com/HAWK-Digital-Environments/HAWKI
