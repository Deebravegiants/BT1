# [H] Hax CMS Stored Cross-Site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-2vc4-3hx7-v7v7
CVE: CVE-2025-49137
CWE: CWE-79, CWE-80, CWE-87
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-2vc4-3hx7-v7v7
Type: github-advisory

## Affected
- Packagist: `elmsln/haxcms` — affected >=0 <11.0.0

## Details
### Summary

The application does not sufficiently sanitize user input, allowing for the execution of arbitrary JavaScript code. The 'saveNode' and 'saveManifest' endpoints take user input and store it in the JSON schema for the site. This content is then rendered in the generated HAX site.

Although the application does not allow users to supply a 'script' tag, it does allow the use of other HTML tags to run JavaScript.

### Affected Resources

- [Operations.php:258](https://github.com/haxtheweb/haxcms-php/blob/master/system/backend/php/lib/Operations.php#L258) `saveManifest()`
- [Operations.php:868](https://github.com/haxtheweb/haxcms-php/blob/master/system/backend/php/lib/Operations.php#L868) `saveNode()`
- `https://<site>/<user>/system/api/saveNode`
- `https://<site>/<user>/system/api/saveManifest`

### Impact

An authenticated attacker can use the site editor and settings editor to store malicious payloads in a HAX site which execute arbitrary JavaScript when a user visits the site. This can be used to steal a user's session cookie or other sensitive data.

### PoCs

#### saveNode

To replicate this vulnerability, an attacker can use the "View Source" functionality within the site editor to enter a malicious payload.

1. Select "View Source" within the HAX site editor and enter an XSS payload that does not use the "script" HTML tag.

![image](https://github.com/user-attachments/assets/c22c52e6-079a-4add-94a2-b51b1a925a96)

3. Select "Update HTML" and observe the resulting alert.

![image](https://github.com/user-attachments/assets/df2da026-de47-4f65-bbc2-c4dbc8fb77e5)

![image](https://github.com/user-attachments/assets/d593418c-73c6-4210-953e-faca8405174c)

#### saveManifest

To exploit the 'SaveManifest' endpoint, an attacker can insert executable code into the URL field of the site settings editor: any payload added this way will execute when the site is loaded.

1. Open the site settings editor.

![image](https://github.com/user-attachments/assets/f7faa998-58ec-4085-9c65-d6a9f3831587)

3. Add JavaScript code to the URL field under the "Theme" header.

![image](https://github.com/user-attachments/assets/a99a7238-bb63-408c-8ca7-22deaffeca83)

5. Reload the page to run the script.

![image](https://github.com/user-attachments/assets/e634b1f3-58c1-44f6-8c8a-814773e69e83)

7. The resulting page source will contain the script.

![image](https://github.com/user-attachments/assets/a022d9d2-a6bf-41ad-a9f2-44a6a2f0fa07)

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-2vc4-3hx7-v7v7
- https://nvd.nist.gov/vuln/detail/CVE-2025-49137
- https://github.com/haxtheweb/haxcms-php/commit/0dd3e98fe2fadd0793b667d4af2aac230980e0f8
- https://github.com/haxtheweb/issues
