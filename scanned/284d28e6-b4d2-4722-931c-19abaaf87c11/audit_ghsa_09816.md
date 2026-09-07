# [H] File Browser: Proxy auth auto-provisioned users inherit Execute permission and Commands

## Summary
Severity: High
Advisory: GHSA-7526-j432-6ppp
CVE: CVE-2026-35607
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-7526-j432-6ppp
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.1

## Details
## Summary

The fix in commit `b6a4fb1` ("self-registered users don't get execute perms") stripped `Execute` permission and `Commands` from users created via the signup handler. The same fix was not applied to the proxy auth handler. Users auto-created on first successful proxy-auth login are granted execution capabilities from global defaults, even though the signup path was explicitly changed to prevent execution rights from being inherited by automatically provisioned accounts.

Confirmed on v2.62.2 (commit 860c19d).

## Root Cause

`auth/proxy.go` `createUser()` applies defaults without restriction:

    user := &users.User{
        Username:     username,
        Password:     hashedRandomPassword,
        LockPassword: true,
    }
    setting.Defaults.Apply(user)
    // No restriction on Execute, Commands, or Admin

Compare with `http/auth.go` signup handler (lines 170-178):

    d.settings.Defaults.Apply(user)
    user.Perm.Admin = false
    // Self-registered users should not inherit execution capabilities
    // from default settings, regardless of what the administrator has
    // configured as the default.
    user.Perm.Execute = false
    user.Commands = []string{}

The commit message for `b6a4fb1` states: "Execution rights must be explicitly granted by an admin." Users auto-created via proxy auth are also automatically provisioned (created on first login without explicit admin action), and the admin has not explicitly granted them execution rights.

## PoC

Tested on filebrowser v2.62.2, built from HEAD.

    # Configure with proxy auth, default commands, and exec
    filebrowser config set --auth.method=proxy --auth.header=X-Remote-User \
      --commands "git,ls,cat,id"

    # Login as admin and verify defaults have execute=true, commands set
    ADMIN_TOKEN=$(curl -s http://HOST/api/login -H "X-Remote-User: admin")

    # Auto-create new user via proxy header
    PROXY_TOKEN=$(curl -s http://HOST/api/login -H "X-Remote-User: newproxyuser")

    # Check permissions
    curl -s http://HOST/api/users -H "X-Auth: $ADMIN_TOKEN" | jq '.[] | select(.username=="newproxyuser") | {execute: .perm.execute, commands}'

Result:

    {
      "execute": true,
      "commands": ["git", "ls", "cat", "id"]
    }

The auto-created proxy user inherited Execute and the full Commands list. A user created via signup would have `execute: false` and `commands: []`.

## Impact

In proxy-auth deployments where the admin has configured default commands, users auto-provisioned on first proxy login receive execution capabilities that were not explicitly granted. The project established a security invariant in commit `b6a4fb1`: automatically provisioned accounts must not inherit execution rights from defaults. The proxy auto-provisioning path violates that invariant.

This is an incomplete fix for GHSA-x8jc-jvqm-pm3f ("Signup Grants Execution Permissions When Default Permissions Includes Execution"), which addressed the signup handler but not the proxy auth handler.

## Preconditions

- Proxy auth enabled (`--auth.method=proxy`)
- Exec not disabled
- Default settings include non-empty Commands (admin-configured)

## Suggested Fix

Apply the same restrictions as the signup handler:

    setting.Defaults.Apply(user)
    user.Perm.Admin = false
    user.Perm.Execute = false
    user.Commands = []string{}

---

**Update:** Fix submitted as PR #5890.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-7526-j432-6ppp
- https://nvd.nist.gov/vuln/detail/CVE-2026-35607
- https://github.com/filebrowser/filebrowser/pull/5890
- https://github.com/filebrowser/filebrowser
