# [C] Authenticated SQL Injection in FreePBX tts (Text To Speech) module

## Summary
Severity: Critical
Advisory: CVE-2025-67736
Aliases: GHSA-632c-49p9-x7cw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-67736
Type: osv

## Details
The FreePBX module tts (Text to Speech) for FreePBX, an open-source web-based graphical user interface (GUI) that manages Asterisk. Versions prior to 16.0.5 and 17.0.5 are vulnerable to SQL injection by authenticated users with administrator access. Authenticated users with administrative access to the Administrator Control Panel (ACP) can leverage this SQL injection vulnerability to extract sensitive information from the database and execute code on the system as the `asterisk` user with chained elevation to `root` privileges. Users should upgrade to version 16.0.5 or 17.0.5 to receive a fix.

## References
- https://www.freepbx.org/watch-what-we-do-with-security-fixes-%f0%9f%91%80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67736.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-632c-49p9-x7cw
- https://nvd.nist.gov/vuln/detail/CVE-2025-67736
