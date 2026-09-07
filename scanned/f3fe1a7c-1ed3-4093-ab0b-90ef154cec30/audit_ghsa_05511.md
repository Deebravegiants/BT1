# [C] Saltcorn's Reflected XSS and Command Injection vulnerabilities can be chained for 1-click-RCE

## Summary
Severity: Critical
Advisory: GHSA-cr3w-cw5w-h3fj
CWE: CWE-77, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-cr3w-cw5w-h3fj
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=1.1.1 <1.5.0-beta.19

## Details
### Summary
1. There is a reflected XSS vulnerability in the GET /admin/edit-codepage/:name route through the name parameter. This can be used to hijack the session of an admin if they click a specially crafted link.
2. Additionally, there is a Command Injection vulnerability in GET /admin/backup. The admin can inject a shell command in the backup password which is inserted in the command used to create the backup zip.


Both vulnerabilities can be chained to craft a malicious link which will execute an arbitrary shell command on the server if it is clicked by a saltcorn admin with an active session. I believe iframes could also be used to exploit this silently when the admin visits an attacker-controlled web page (though I have not tested that).

### Details
1. The XSS vulnerability is here: https://github.com/saltcorn/saltcorn/blob/020893c0001678fd5ebd2c088ba68b395de1aabc/packages/server/routes/admin.js#L4886-L4887 Specifically, the name parameter is inserted into the pages breadcrumbs without sanitization.
2. The Command Injection happens here: https://github.com/saltcorn/saltcorn/blob/020893c0001678fd5ebd2c088ba68b395de1aabc/packages/saltcorn-admin-models/models/backup.ts#L381-L382

### PoC
1. A minimal PoC for the XSS can be as simple as: http://localhost:3000/admin/edit-codepage/%3Cimg%20src%3Dx%20onerror%3Dalert%281%29%3E%0A (assuming saltcorn running at localhost:3000 and the user having an active admin session)
2. For the Command Injection, visit the backup section of saltcorn, set an admin password like `";$(whoami);"` (including the quotation marks) and then click "Download a backup" in the "Manual backup" section. This should display an error page saying that /bin/sh could not find the binary named "root" or "saltcorn", depending on the user.

An example of an exploit that chains both vulnerabilities and generates the aforementioned malicious link:
[exploit.zip](https://github.com/user-attachments/files/24356819/exploit.zip)

### Affected Versions
Edit: The following Docker containers from docker hub were tested: 1.4.1, 1.4.0, 1.3.1, 1.3.0, 1.2.0, 1.1.2, 1.1.1, 1.0.0
The Command Injection is applicable to versions >= 1.3.0.
The XSS is applicable to versions >= 1.1.1

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-cr3w-cw5w-h3fj
- https://github.com/saltcorn/saltcorn/commit/1bf681e08c45719a52afcf3506fb5ec59f4974d5
- https://github.com/saltcorn/saltcorn
- https://github.com/saltcorn/saltcorn/blob/020893c0001678fd5ebd2c088ba68b395de1aabc/packages/saltcorn-admin-models/models/backup.ts#L381-L382
- https://github.com/saltcorn/saltcorn/blob/020893c0001678fd5ebd2c088ba68b395de1aabc/packages/server/routes/admin.js#L4886-L4887
