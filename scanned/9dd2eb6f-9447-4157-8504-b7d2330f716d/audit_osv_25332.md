# [H] Collabora Online has Stored Cross-Site-Scripting vulnerability in admin interface

## Summary
Severity: High
Advisory: CVE-2023-34088
Aliases: GHSA-7582-pwfh-3pwr
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-05-31
Source: https://osv.dev/vulnerability/CVE-2023-34088
Type: osv

## Details
Collabora Online is a collaborative online office suite. A stored cross-site scripting (XSS) vulnerability was found in Collabora Online prior to versions 22.05.13, 21.11.9.1, and 6.4.27. An attacker could create a document with an XSS payload as a document name. Later, if an administrator opened the admin console and navigated to the history page, the document name was injected as unescaped HTML and executed as a script inside the context of the admin console. The administrator JSON web token (JWT) used for the websocket connection could be leaked through this flaw. Users should upgrade to Collabora Online 22.05.13 or higher; Collabora Online 21.11.9.1 or higher; Collabora Online 6.4.27 or higher to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34088.json
- https://github.com/CollaboraOnline/online/security/advisories/GHSA-7582-pwfh-3pwr
- https://nvd.nist.gov/vuln/detail/CVE-2023-34088
