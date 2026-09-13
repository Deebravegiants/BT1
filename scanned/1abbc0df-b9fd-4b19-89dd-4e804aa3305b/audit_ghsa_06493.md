# [M] Froxlor: Authenticated customers can read other customers' allowed sender aliases

## Summary
Severity: Medium
Advisory: GHSA-mr9h-45p9-fg8h
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-mr9h-45p9-fg8h
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.7

## Details
## Summary

An authenticated customer can read other customers' allowed sender aliases from Froxlor's sender-delete confirmation page when `mail.enable_allow_sender` is enabled. `customer_email.php` loads `allowed_sender` by global auto-increment `senderid` alone, so a customer can enumerate foreign sender alias IDs and make Froxlor disclose those values in the confirmation dialog for the attacker's own mailbox.

## Details

The vulnerable read lives in `customer_email.php`:

```php
$senderid = Request::any('senderid', 0);
...
$sel_stmt = Database::prepare("SELECT `allowed_sender` FROM `" . TABLE_MAIL_SENDER_ALIAS . "` WHERE `id` = :sid");
$sender_data = Database::pexecute_first($sel_stmt, ['sid' => $senderid]);

HTML::askYesNo('email_reallydelete_sender', $filename, [
    'id' => $id,
    'senderid' => $senderid,
    'page' => $page,
    'domainid' => $email_domainid,
    'action' => $action
], $idna_convert->decode($result['email_full']) . ' -> ' . $sender_data['allowed_sender']);
```

The query does not scope `senderid` to the current customer or to the mailbox being edited. `mail_sender_aliases.id` is a global `AUTO_INCREMENT` primary key:

```sql
CREATE TABLE `mail_sender_aliases` (
  `id` int(11) NOT NULL auto_increment,
  `email` varchar(255) NOT NULL,
  `allowed_sender` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`)
)
```

That makes sender alias IDs enumerable. A customer who owns any mailbox with sender-alias management enabled can request the delete-confirmation page for their own mailbox while supplying foreign `senderid` values. Froxlor then renders the foreign `allowed_sender` string in the confirmation prompt.

## Proof of Concept

Verified against Froxlor `2.3.6` on a fresh test install with `mail.enable_allow_sender=1`.

1. Create two customers, `victim` and `attacker`.
2. Give each customer one mailbox.
3. Add a sender alias for the victim mailbox:

```text
info@victim.local -> leaked-sender@example.org
```

4. Log in as the attacker and request the delete-confirmation page for the attacker's own mailbox while supplying the victim's sender alias ID:

```text
/customer_email.php?page=senders&domainid=4&action=delete&id=2&senderid=1
```

Observed in the live test instance:

```text
Do you really want to delete the allowed sender info@attacker.local -> leaked-sender@example.org?
```

The attacker-controlled mailbox identifier stayed `info@attacker.local`, but the disclosed sender alias text came from the victim-owned row identified by `senderid=1`.

## Impact

An authenticated customer can enumerate global sender alias IDs and read other customers' allowed sender values. This is a cross-tenant information disclosure. It does not let the attacker delete the foreign alias because the delete action revalidates ownership.

## Recommended Fix

Scope the sender alias lookup to the current customer and mailbox before rendering the confirmation page. The confirmation flow should fetch the sender alias through the same ownership checks used by `EmailSender::delete()`.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-mr9h-45p9-fg8h
- https://github.com/froxlor/froxlor
