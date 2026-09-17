# [H] Yeswiki Path Traversal vulnerability allows arbitrary read of files

## Summary
Severity: High
Advisory: GHSA-w34w-fvp3-68xm
CVE: CVE-2025-31131
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-w34w-fvp3-68xm
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.5.2

## Details
### Summary
The `squelette` parameter is vulnerable to path traversal attacks, enabling read access to arbitrary files on the server. The payload `../../../../../../etc/passwd` was submitted in the `squelette` parameter. The requested file was returned in the application's response.

### Details
File path traversal vulnerabilities arise when user-controllable data is used within a filesystem operation in an unsafe manner. Typically, a user-supplied filename is appended to a directory prefix in order to read or write the contents of a file. If vulnerable, an attacker can supply path traversal sequences (using dot-dot-slash characters) to break out of the intended directory and read or write files elsewhere on the filesystem.

### PoC
1. Access the below URL to see the contents of `/etc/passwd`:
   **URL with payload:** `https://yeswiki.net/?UrkCEO/edit&theme=margot&squelette=..%2f..%2f..%2f..%2f..%2f..%2fetc%2fpasswd&style=margot.css`
   
   Similarly, contents of `wakka.config.php` can be read (which contains database password) using `..%2f..%2f..%2fwakka.config.php` as payload. Thus showing the severity of this issue. 

### Impact
This is a very serious vulnerability, allowing an attacker to access sensitive files containing configuration data, passwords, database records, log data, source code, and program scripts and binaries. Thus, leading to complete loss of confidentiality.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-w34w-fvp3-68xm
- https://nvd.nist.gov/vuln/detail/CVE-2025-31131
- https://github.com/YesWiki/yeswiki/commit/f78c915369a60c74ab8f38561ae93a4aaca9b989
- https://github.com/YesWiki/yeswiki
