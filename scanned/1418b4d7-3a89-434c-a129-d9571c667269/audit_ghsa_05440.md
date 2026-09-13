# [M] PsySH has Local Privilege Escalation via CWD .psysh.php auto-load

## Summary
Severity: Medium
Advisory: GHSA-4486-gxhx-5mg7
CVE: CVE-2026-25129
CWE: CWE-427
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-4486-gxhx-5mg7
Type: github-advisory

## Affected
- Packagist: `psy/psysh` — affected >=0.12.0 <0.12.19
- Packagist: `psy/psysh` — affected >=0 <0.11.23

## Details
### Summary
PsySH automatically loads and executes a `.psysh.php` file from the Current Working Directory (CWD) on startup. If an attacker can write to a directory that a victim later uses as their CWD when launching PsySH, the attacker can trigger arbitrary code execution in the victim's context. When the victim runs PsySH with elevated privileges (e.g., root), this results in local privilege escalation.

### Details
PsySH supports per-directory configuration via a `.psysh.php` file located in the process CWD. This file is executed implicitly when PsySH starts, without requiring explicit opt-in and without validating that the file and directory are safe (e.g., owned by the current user and not group/world-writable).

This enables a CWD poisoning scenario: a low-privileged user can plant a malicious `.psysh.php` in any directory they can write to, then wait for a higher-privileged user to start PsySH while their shell is in that directory.

### PoC
1. As a low-privileged user, create a malicious `.psysh.php` in an attacker-writable directory (example: `/tmp`):

```bash
bob@localhost:/tmp$ echo "<?php system('id > poc.txt'); ?>" > .psysh.php
bob@localhost:/tmp# ls -lah .psysh.php
-rw-r--r-- 1 bob bob 33 Jan 28 11:17 .psysh.php
```

2. As the victim user, start PsySH with CWD set to that directory and exit:

```bash
root@localhost:/tmp# cd /tmp
root@localhost:/tmp# ./psysh
Psy Shell v0.12.18 (PHP 8.1.2-1ubuntu2.23 — cli) by Justin Hileman
New PHP manual is available (latest: 3.0.1). Update with `doc --update-manual`
> exit

   INFO  Goodbye.

```

3. Verify code execution triggered in the victim context:

```bash
bob@localhost:/tmp$ ls -lah poc.txt
-rw-r--r-- 1 root root 39 Jan 28 11:19 poc.txt
bob@localhost:/tmp$ cat poc.txt
uid=0(root) gid=0(root) groups=0(root)
````


### Impact

This is a CWD configuration poisoning issue leading to arbitrary code execution in the victim user’s context. If a privileged user (e.g., root, a CI runner, or an ops/debug account) launches PsySH with CWD set to an attacker-writable directory containing a malicious `.psysh.php`, the attacker can execute commands with that privileged user’s permissions, resulting in local privilege escalation.

Downstream consumers that embed PsySH inherit this risk. For example, Laravel Tinker (`php artisan tinker`) uses PsySH. If a privileged user runs Tinker while their shell is in an attacker-writable directory, the `.psysh.php` auto-load behavior can be abused in the same way to execute attacker-controlled code under the victim’s privileges.

## References
- https://github.com/bobthecow/psysh/security/advisories/GHSA-4486-gxhx-5mg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25129
- https://github.com/bobthecow/psysh
- https://github.com/bobthecow/psysh/releases/tag/v0.11.23
- https://github.com/bobthecow/psysh/releases/tag/v0.12.19
