# [H] Backend Same-Site Request Forgery in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-pqg8-crx9-g8m4
CVE: CVE-2020-11069
CWE: CWE-346, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-pqg8-crx9-g8m4
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.17
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.17

## Details
> ### Meta
> * CVSS v3.1: AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C
> * CWE-352
> * CWE-346

### Problem
It has been discovered that backend user interface and install tool are vulnerable to same-origin request forgery. A backend user can be tricked into interacting with a malicious resource an attacker previously managed to upload to the web server - scripts are then executed with the privileges of the victims' user session.

In a worst case scenario new admin users can be created which can directly be used by an attacker. The vulnerability is basically a cross-site request forgery (CSRF) triggered by a cross-site scripting vulnerability (XSS) - but happens on the same target host - thus, it’s actually a same-origin request forgery.

Malicious payload such as HTML containing JavaScript might be provided by either an authenticated backend user or by a non-authenticated user using a 3rd party extension - e.g. file upload in a contact form with knowing the target location.

The attacked victim requires an active and valid backend or install tool user sessions at the time of the attack to be successful.

### Solution
Update to TYPO3 versions 9.5.17 or 10.4.2 that mitigates the problem described.

### Additional Considerations

The deployment of additional mitigation techniques is suggested as described below.

#### Sudo Mode Extension

This TYPO3 extension intercepts modifications to security relevant database tables, e.g. those storing user accounts or storages of the file abstraction layer. Modifications need to confirmed by again by the acting user with providing their password again - this technique is known as "sudo mode". This way unintended actions happening in the background can be mitigated.

* https://github.com/FriendsOfTYPO3/sudo-mode
* https://extensions.typo3.org/extension/sudo_mode

#### Content Security Policy

[Content Security Policies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy) tell (modern) browsers how resources served a particular site are handled - it also it possible to disallow script executions for specific locations. In a TYPO3 context it is suggested to disallow direct script execution at least for locations `/fileadmin/` and `/uploads/`.

```
# in fileadmin/.htaccess
<IfModule mod_headers.c>
	Header add Content-Security-Policy "default-src 'self'; script-src 'none';"
</IfModule>
```

### Credits
Thanks to Matteo Bonaker who reported this issue and to TYPO3 security team member Oliver Hader who fixed the issue.

### References
* https://typo3.org/security/advisory/typo3-core-sa-2020-006

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-pqg8-crx9-g8m4
- https://nvd.nist.gov/vuln/detail/CVE-2020-11069
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-11069.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-11069.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2020-006
