# [M] Craft CMS: Sensitive File Disclosure / Server-Side File Read

## Summary
Severity: Medium
Advisory: GHSA-287w-mxq6-x2cp
CVE: CVE-2026-55792
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-287w-mxq6-x2cp
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.0
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.0

## Details
The `dataUrl()` Twig function is included in Craft’s Twig sandbox allowlist, allowing any control panel user granted the `utility:system-messages` permission to embed a file-reading payload into system email templates. When those emails are sent, the server reads the target file and returns its contents as a base64-encoded data URL embedded in the email body. The .env file, which typically contains the database password, CRAFT_SECURITY_KEY, and third-party API keys, passes all of Craft’s existing `dataUrl()` protection checks and is fully exfiltrated. Obtaining CRAFT_SECURITY_KEY enables an attacker to forge session tokens and escalate to full admin account takeover.

## Details
Affected versions: Craft CMS 4.x, 5.x (confirmed against 5.9.19)

The vulnerability arises from the combination of three code facts:
1. dataUrl is in the Twig sandbox allowlist
src/config/twig-sandbox.php, line 115:
php'allowedFunctions' => [
    ...
    'dataUrl',   // ← allows file reading inside sandboxed templates
    ...
],

2. Html::dataUrl() does not block dotfiles
src/helpers/Html.php, lines 1065–1090. The function applies four checks before reading a file:

Must be within the project root .env is at the root
Must not be in a system directory (config/, vendor/, storage/, templates/) .env is not
Must not be a .php file  .env has no extension
File must exist .env always exists in a Craft install

There is no check for dotfiles or specifically for .env. All four checks pass silently and file_get_contents() is called, with the result returned as data:text/plain;base64,....

3. System message body is rendered via renderSandboxedString()
src/mail/Mailer.php, lines 181–183:
php$subject = $view->renderSandboxedString($systemMessage->subject, $variables);
$textBody = $view->renderSandboxedString($systemMessage->body, $variables);
$htmlBody = $view->renderSandboxedString($systemMessage->body, $variables, escapeHtml: true);

Any body content saved to a system message is executed inside the Twig sandbox when the email renders. Because dataUrl is in allowedFunctions, the sandbox policy permits its execution without restriction.

Access control: The utility:system-messages permission is a non-admin CP permission grantable to any user group via Settings > Users > Groups. It is not restricted to admins.

## Impact
Vulnerability type: Sensitive File Disclosure / Server-Side File Read
Who is impacted: Any Craft CMS 4.x or 5.x installation where at least one non-admin control panel user has been granted the utility:system-messages permission, and email sending is configured.

Resources:

- https://github.com/craftcms/cms/pull/18559

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-287w-mxq6-x2cp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55792
- https://github.com/craftcms/cms/pull/18559
- https://github.com/craftcms/cms
