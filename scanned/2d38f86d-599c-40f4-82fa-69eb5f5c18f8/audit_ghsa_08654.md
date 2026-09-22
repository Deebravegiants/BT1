# [H] Froxlor has an authorization bypass in FTP shell assignment via missing server-side `available_shells` enforcement

## Summary
Severity: High
Advisory: GHSA-gcv3-5v9q-fmhh
CVE: CVE-2026-41235
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-gcv3-5v9q-fmhh
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=2.3.6 <2.3.7

## Details
### Summary
Froxlor 2.3.6 lets administrators configure `system.available_shells` as the approved shell list that customers may assign to FTP users. However, the server-side FTP account handlers do not enforce that whitelist when processing add or edit requests.

As a result, an authenticated customer with shell delegation enabled can submit an arbitrary shell such as `/bin/bash` even when the panel UI only offers more restricted choices. In deployments that use the default `nssextrausers` integration, the attacker-controlled shell is then propagated into the system account database, leading to real host shell access.

### Details
The customer-facing FTP account page builds the shell selector from `system.available_shells`, which shows that the product intends the setting to act as the authorization boundary:

```php
// customer_ftp.php:138-149
$shells = [
    '/bin/false' => '/bin/false'
];
$availableshells = explode(',', Settings::Get('system.available_shells'));
if (is_array($availableshells) && !empty($availableshells)) {
    foreach ($availableshells as $shell) {
        $shells[trim($shell)] = trim($shell);
    }
}
```

The request handler forwards posted form data directly into the FTP API command implementation:

```php
// customer_ftp.php:170-172
if ($action == 'edit' && Request::post('send') == 'send') {
    $result = $log->logAction(USR_ACTION, LOG_INFO, "edited ftp-account #" . $id);
    Commands::get()->apiCall('Ftps.update', Request::postAll());
}
```

On the server side, `Ftps::add()` and `Ftps::update()` only perform generic shell string validation. They do not verify that the submitted shell belongs to `system.available_shells`:

```php
// lib/Froxlor/Api/Commands/Ftps.php:119-123
if (Settings::Get('system.allow_customer_shell') == '1' && $this->getUserDetail('shell_allowed') == '1') {
    $shell = Validate::validate(trim($shell), 'shell', '', '', [], true);
} else {
    $shell = '/bin/false';
}
```

The validated shell is stored into `ftp_users.shell` and later consumed by the root-owned cron task that rebuilds NSS extrausers files:

```php
// lib/Froxlor/Cron/System/Extrausers.php:89-97
$passwd_entries[] = $user['username'] . ':x:' . $uid . ':' . $gid . ':' . $gecos . ':' . $homedir . ':' . $shell;
```

Because the default installer configuration sets `system.nssextrausers=1`, and the shipped Debian/Bookworm configuration enables `extrausers` in `nsswitch.conf`, the attacker-controlled shell becomes the effective login shell of the generated system user on standard supported deployments.

### PoC
An attacker needs a normal customer account and a deployment where customer shell delegation is enabled for that customer.

Relevant runtime prerequisites:

- `system.allow_customer_shell=1`
- the attacking customer has `shell_allowed=1`
- the deployment uses `system.nssextrausers=1` with the shipped `libnss-extrausers` integration

Froxlor requires a valid CSRF token for POST requests, so the attacker performs the exploit from an authenticated session.

Complete PoC flow:

1. Log in as a customer and obtain a valid `csrf_token`.
2. Identify one FTP account owned by that customer.
3. Submit an edit request that sets an arbitrary shell outside the administrator-approved `system.available_shells` list:

```http
POST /customer_ftp.php?page=accounts&action=edit&id=17 HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Cookie: <authenticated customer session>

csrf_token=VALID_CSRF_TOKEN&
send=send&
id=17&
username=test1ftp1&
ftp_description=poc&
path=/&
shell=/bin/bash&
login_enabled=1
```

4. Wait for Froxlor's master cron to process the queued `REBUILD_NSSUSERS` task.

Result:

- the request is accepted even if `/bin/bash` is not present in `system.available_shells`
- `ftp_users.shell` is updated to `/bin/bash`
- `/var/lib/extrausers/passwd` is regenerated with `/bin/bash` as the FTP user's login shell
- the attacker can then authenticate to the host using that FTP user's credentials and obtain an interactive shell


### Impact
This issue lets a low-privileged customer bypass an administrator-defined authorization boundary and promote an FTP-only account into a real shell account. On shared-hosting systems managed by Froxlor, that materially changes the trust model and can expose the host to lateral movement, local privilege-escalation follow-on attacks, data theft from colocated services, and persistence on the server.

Because the vulnerable flow is executed through the normal authenticated web interface and a root-owned provisioning task later materializes the chosen shell at the operating-system level, the vulnerability is stronger than a UI-only restriction bypass.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-gcv3-5v9q-fmhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41235
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.7
