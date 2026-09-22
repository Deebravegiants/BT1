# [M] AVideo: HTML Injection in notifySubscribers.json.php Allows Platform-Branded Phishing Emails to Channel Subscribers

## Summary
Severity: Medium
Advisory: GHSA-g9cm-rxp7-6gv5
CVE: CVE-2026-43876
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-g9cm-rxp7-6gv5
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`objects/notifySubscribers.json.php` takes the raw `message` POST parameter and passes it into `sendSiteEmail()`, which substitutes it directly into an HTML email template (via `str_replace` on the `{message}` placeholder) and renders it with `PHPMailer::msgHTML()`. There is no HTML sanitization, character escaping, or output encoding on the attacker-controlled `message` between `$_POST['message']` and the rendered email. Any authenticated user with upload permission can therefore broadcast arbitrary HTML — phishing links, tracking pixels, CSS/UI spoofing — to every subscriber on their channel (up to 10,000 recipients per invocation). The email is sent From: the platform's configured contact address and wrapped in the site's official logo and title, so attacker-supplied HTML arrives with the appearance of an official platform communication.

## Details

**File:** `objects/notifySubscribers.json.php`

```php
10: if (!User::canUpload()) {
11:     forbiddenPage('You can not notify');
12: }
13: forbidIfIsUntrustedRequest('notifySubscribers');
14: $user_id = User::getId();
15: // if admin bring all subscribers
16: if (User::isAdmin()) {
17:     $user_id = '';
18: }
19:
20: require_once 'subscribe.php';
21: setRowCount(10000);
...
23: $Subscribes = Subscribe::getAllSubscribes($user_id);
...
34: $subject = 'Message From Site ' . $config->getWebSiteTitle();
35: $message = $_POST['message'];
36:
37: $resp = sendSiteEmail($to, $subject, $message);
```

Controls present at the entry point:

- `User::canUpload()` — gates access to any account that can upload (a baseline authenticated uploader role; in typical AVideo configurations where `authCanUploadVideos` is enabled, this is any logged-in user with a verified email).
- `forbidIfIsUntrustedRequest('notifySubscribers')` — in `objects/functionsSecurity.php:138-165`, this delegates to `isUntrustedRequest()` which only validates same-origin via `requestComesFromSameDomainAsMyAVideo()` (`objects/functionsAVideo.php:199-206`), i.e. a Referer/Origin header check. It is **not** a CSRF token. An attacker acting on their own authenticated browser session trivially satisfies the Referer check.

There is no CAPTCHA, no rate limit, no per-recipient quota, and no unsubscribe link. `setRowCount(10000)` allows up to 10,000 subscriber rows to be pulled and mailed in a single request. For admin callers (`User::isAdmin()` → `$user_id = ''`), `Subscribe::getAllSubscribes('')` returns the entire subscriber set for the platform rather than the caller's channel.

**File:** `objects/functionsMail.php`

```php
 59: function sendSiteEmail($to, $subject, $message, $fromEmail = '', $fromName = '')
 60: {
 ...
 78:     $subject = UTF8encode($subject);
 79:     $message = UTF8encode($message);            // UTF-8 normalization, no HTML handling
 80:     $message = createEmailMessageFromTemplate($message);
 ...
119:             $mail = new \PHPMailer\PHPMailer\PHPMailer();
120:             setSiteSendMessage($mail);
...
125:             $systemEmail = $config->getContactEmail();
126:             $systemName  = $config->getWebSiteTitle();
...
136:             $mail->setFrom($systemEmail, !empty($fromName) ? $fromName : $systemName);
...
143:             $mail->msgHTML($message);           // renders as HTML
...
162:             $resp = $mail->send();
```

```php
266: function createEmailMessageFromTemplate($message)
267: {
268:     if (preg_match("/html>/i", $message)) {
269:         return $message;                       // attacker-supplied full-HTML is returned verbatim
270:     }
...
274:     $text = file_get_contents("{$global['systemRootPath']}view/include/emailTemplate.html");
...
279:     $words   = [$logo, $message, $siteTitle];
280:     $replace = ['{logo}', '{message}', '{siteTitle}'];
281:
282:     return str_replace($replace, $words, $text);   // raw substitution into HTML template
283: }
```

Execution flow from attacker input to sink:

1. `$_POST['message']` → `objects/notifySubscribers.json.php:35` (raw, no validation).
2. → `sendSiteEmail($to, $subject, $message)` at `objects/notifySubscribers.json.php:37`.
3. → `UTF8encode($message)` at `objects/functionsMail.php:79` (encoding only; does not strip or escape HTML).
4. → `createEmailMessageFromTemplate($message)` at `objects/functionsMail.php:80` → `str_replace('{message}', $message, $text)` at `objects/functionsMail.php:282`, substituting attacker HTML directly into the `{message}` placeholder in `view/include/emailTemplate.html`.
5. → `$mail->msgHTML($message)` at `objects/functionsMail.php:143`. PHPMailer renders the combined template (containing the attacker's unsanitized HTML) as an HTML email.
6. The `From:` header is `$config->getContactEmail()` / `$config->getWebSiteTitle()` (`objects/functionsMail.php:125-136`). The template contains the platform's logo via `getURL($config->getLogo())`. The result is an attacker-controlled HTML body delivered from the platform's trusted sender address, officially branded.

Note that the `preg_match("/html>/i", $message)` at line 268 actively *helps* the attacker: any payload containing `<html>` short-circuits template substitution and is sent as-is, allowing the attacker to control the full email body including DOCTYPE, head, and body.

## PoC

1. Obtain an account with upload permission (on AVideo installations where `authCanUploadVideos` is enabled, any registered and email-verified user qualifies). An admin account broadens the recipient set to the entire platform rather than just the attacker's own subscribers.
2. Ensure the attacker's channel has at least one subscriber (via `Subscribe::getAllSubscribes($user_id)`), or use an admin account to target all platform subscribers.
3. Submit the request. The `Referer` header must match the platform origin to pass `forbidIfIsUntrustedRequest` (trivial when running from the attacker's own authenticated browser):

```bash
curl -b 'PHPSESSID=<uploader_session>' -X POST \
  -H 'Referer: https://target.example/' \
  'https://target.example/objects/notifySubscribers.json.php' \
  --data-urlencode 'message=<h1 style="color:#c00">Action Required: Verify Your Account</h1>
<p>Dear Subscriber,</p>
<p>We detected unusual activity on your account. Please
<a href="https://attacker.example/phish">click here to verify your identity within 24 hours</a>
or your account will be suspended.</p>
<p>Thank you,<br>The Support Team</p>
<img src="https://attacker.example/track.png" width="1" height="1">'
```

4. Expected response:

```json
{"error": false, "msg": ""}
```

5. Every subscriber in the target set receives an HTML email:
   - `From:` `<contact@target.example>` (the platform's configured contact email — not the attacker's address).
   - `Subject:` `Message From Site <SiteTitle> - <SiteTitle>` (built at `objects/notifySubscribers.json.php:34` + `objects/functionsMail.php:138-141`).
   - Body: the `view/include/emailTemplate.html` template with the platform's real logo substituted at `{logo}` and the attacker's unsanitized HTML substituted at `{message}`, including the phishing anchor and tracking pixel.

6. Delivery is batched via `partition($to, $size)` at `objects/functionsMail.php:114-118` over up to 10,000 subscribers in a single request. There is no rate limit, CAPTCHA, confirmation step, or unsubscribe header.

## Impact

- Any authenticated uploader can weaponize the platform's own email infrastructure and brand (contact email, logo, site title) to deliver phishing content to their channel subscribers.
- Because the `From:` address is the platform's canonical contact email and the template wraps the attacker content in the official logo and site title, recipients have no visible indication that the content originated from an uploader rather than the operator. Recipients who have previously received legitimate notifications from the same address are especially likely to trust the email.
- Phishing payloads can include credential-stealing links mimicking password reset / account verification flows, tracking pixels that enumerate subscriber IPs and mail-client metadata, and CSS-based UI spoofing over the template.
- An admin account (`User::isAdmin()` → `$user_id = ''`) expands the blast radius to every subscriber record on the platform, not just the attacker's own subscribers.
- Up to 10,000 recipients per request with no rate limiting, CAPTCHA, or unsubscribe link, so a compromised or malicious uploader can sustain large phishing campaigns at minimal cost, while the sending IP reputation is borne by the platform operator.
- A stolen uploader session (e.g., via an unrelated XSS or token leak) is sufficient to mount the attack; no additional credentials or admin access are required.

## Recommended Fix

Sanitize or encode `$_POST['message']` before it reaches `PHPMailer::msgHTML()`. Options, in order of preference:

1. **Reject HTML outright** and force plain text. In `objects/notifySubscribers.json.php`:

   ```php
   $message = $_POST['message'] ?? '';
   // Strip all HTML; allow only newlines / plain text.
   $message = strip_tags($message);
   $message = nl2br(htmlspecialchars($message, ENT_QUOTES | ENT_HTML5, 'UTF-8'));
   ```

2. **Or** allow a very restricted subset using a proven HTML sanitizer (e.g. `HTMLPurifier` with a minimal whitelist: `p, br, strong, em, a[href|title], ul, ol, li`), and forbid `<script>`, `<style>`, inline event handlers, `<img>`, `<iframe>`, `data:`/`javascript:` URIs, and framework-style template tokens.

3. **Additionally** remove the `preg_match("/html>/i", $message)` short-circuit at `objects/functionsMail.php:268-270`, which lets a caller replace the entire email body by including a `<html>` tag. The template should always be applied.

4. **Defense in depth:**
   - Require a real anti-CSRF token on this endpoint (e.g. `validateCSRF()` with a per-session token in a header or POST field), and drop the Referer-only `forbidIfIsUntrustedRequest` as the sole protection.
   - Require `User::isAdmin()` to notify subscribers from accounts not scoped to a channel; for non-admin uploaders, make the `From` display name clearly attribute the message to the uploader (`"{uploaderName} via {siteTitle} <contact@site>"` already works for non-system senders in `objects/functionsMail.php:130-134` — apply the same attribution to subscriber notifications).
   - Enforce per-account and per-IP rate limits on `notifySubscribers.json.php` (e.g. one broadcast per account per N hours, max M recipients per day).
   - Include a List-Unsubscribe header and a per-recipient unsubscribe link.
   - Add a preview + confirmation step before dispatch.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-g9cm-rxp7-6gv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-43876
- https://github.com/WWBN/AVideo/commit/078c4342eb9969a70425a9cdca3eefa7f8a86d53
- https://github.com/WWBN/AVideo
