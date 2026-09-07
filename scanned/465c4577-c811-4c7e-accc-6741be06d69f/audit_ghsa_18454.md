# [C] CodeIgniter4's ImageMagick Handler has Command Injection Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9952-gv64-x94c
CVE: CVE-2025-54418
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-28
Source: https://github.com/advisories/GHSA-9952-gv64-x94c
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.6.2

## Details
### Impact
This vulnerability affects applications that:
* Use the ImageMagick handler for image processing (`imagick` as the image library)
* **AND** either:
  * Allow file uploads with user-controlled filenames and process uploaded images using the `resize()` method
  * **OR** use the `text()` method with user-controlled text content or options

An attacker can:
* Upload a file with a malicious filename containing shell metacharacters that get executed when the image is processed
* **OR** provide malicious text content or options that get executed when adding text to images

### Patches
Upgrade to v4.6.2 or later.

### Workarounds
* **Switch to the GD image handler** (`gd`, the default handler), which is not affected by either vulnerability
* **For file upload scenarios**: Instead of using user-provided filenames, generate random names to eliminate the attack vector with `getRandomName()` when using the `move()` method, or use the `store()` method, which automatically generates safe filenames
* **For text operations**: If you must use ImageMagick with user-controlled text, sanitize the input to only allow safe characters: `preg_replace('/[^a-zA-Z0-9\s.,!?-]/', '', $text)` and validate/restrict text options


### References
* [OWASP Command Injection Prevention](https://owasp.org/www-community/attacks/Command_Injection)
* [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-9952-gv64-x94c
- https://nvd.nist.gov/vuln/detail/CVE-2025-54418
- https://github.com/codeigniter4/CodeIgniter4/commit/e18120bff1da691e1d15ffc1bf553ae7411762c0
- https://cwe.mitre.org/data/definitions/78.html
- https://github.com/codeigniter4/CodeIgniter4
- https://owasp.org/www-community/attacks/Command_Injection
