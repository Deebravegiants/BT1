# [C] screenshot-desktop vulnerable to command Injection via `format` option

## Summary
Severity: Critical
Advisory: GHSA-gjx4-2c7g-fm94
CVE: CVE-2025-55294
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-gjx4-2c7g-fm94
Type: github-advisory

## Affected
- npm: `screenshot-desktop` — affected >=0 <1.15.2

## Details
## Impact
This vulnerability is a **command injection** issue.  
When user-controlled input is passed into the `format` option of the screenshot function, it is interpolated into a shell command without sanitization.  
An attacker can craft malicious input such as:

    { format: "; echo vulnerable > /tmp/hello;" }

This results in arbitrary command execution with the privileges of the calling process.

**Who is impacted:**  
Any application that accepts untrusted input and forwards it directly (or indirectly) into the `format` option is affected. If the library is used in a server-side context (e.g., API endpoints, web services), attackers may be able to exploit this **remotely and without authentication**, leading to full compromise of confidentiality, integrity, and availability.

**CVSS v3.1 Base Score:** 9.8 (Critical)  
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`


## Patches
The issue has been patched in **version 1.15.2**.  
All users are strongly recommended to upgrade to **1.15.2 or later**.  
All earlier versions are vulnerable.



## Workarounds
If upgrading is not immediately possible, developers should:
- **Strictly validate or whitelist** acceptable `format` values (e.g., `"jpeg"`, `"png"`, `"webp"`).
- **Reject or sanitize** any unexpected input before passing it to the library.
- Avoid allowing user-controlled data to reach the `format` option.



## References
- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)  
- [OWASP: Command Injection](https://owasp.org/www-community/attacks/Command_Injection)

## References
- https://github.com/bencevans/screenshot-desktop/security/advisories/GHSA-gjx4-2c7g-fm94
- https://nvd.nist.gov/vuln/detail/CVE-2025-55294
- https://github.com/bencevans/screenshot-desktop/commit/59c87b0c175eec76090e6ccde313f4fc5d569b78
- https://github.com/bencevans/screenshot-desktop
