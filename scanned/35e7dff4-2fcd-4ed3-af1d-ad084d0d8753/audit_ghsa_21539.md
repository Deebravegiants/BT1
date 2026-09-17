# [H] Redwood is vulnerable to account takeover via dbAuth "forgot-password" 

## Summary
Severity: High
Advisory: GHSA-3qmc-2r76-4rqp
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-3qmc-2r76-4rqp
Type: github-advisory

## Affected
- npm: `@redwoodjs/api` — affected >=0.38.0 <2.2.5
- npm: `@redwoodjs/api` — affected >=3.0.0 <3.3.1

## Details
# Impact

_What kind of vulnerability is it? Who is impacted?_

This is an API vulnerability in Redwood's [dbAuth], specifically the dbAuth forgot password feature:
- only projects with the dbAuth "forgot password" feature are affected
- this vulnerability was introduced in v0.38.0

## User Accounts are Vulnerable to Takeover (Hijacking)

A reset token for any user can be obtained given knowledge of their username or email via the forgot-password API. With the leaked reset token, a malicious user could request to reset a user's password, changing their credentials and gaining access to their account.

## How to Determine if Projects have been Attacked

To determine if a project has been attacked, we recommend checking logs for suspicious activity; namely, the volume of requests to the forgot-password API using emails that don't exist. Another indication is if users inform you that they can't access their accounts.

If you have question or concerns, reach out via the "For More Information" section below.

# Patch Releases Available

**The problem has been patched on the v3 and v2 release lines.** Users should upgrade to **v3.3.1+**  or **v2.2.5+** respectively.

## Workarounds

_Is there a way for users to fix or remediate the vulnerability without upgrading?_

We recommend upgrading to the Patch Releases above. If upgrading is not possible, there are several workarounds:

### Manually strip out `resetToken` and `resetTokenExpiresAt` in the `forgotPassword.handler()`

Users on all release lines can have their `forgotPassword.handler()` function strip out the sensitive fields manually before returning

```js
handler: (user) => {
  // your code to notify/email user of the link to reset their password...

  const = { resetToken, resetTokenExpiresAt, ...rest }

  return rest
}
```

### Use `yarn patch` to manually apply the fix

Users on v3 and v2 can use [`yarn patch`] to apply the fix if they're using yarn v3. See the dbAuth "forgot-password" Account Takeover Vulnerability high gist for instructions. 

### Disable the forgot password flow entirely v3 only

Users on v3 can disable the forgot password flow entirely.

## References
- https://github.com/redwoodjs/redwood/security/advisories/GHSA-3qmc-2r76-4rqp
- https://github.com/redwoodjs/redwood/issues/6343
- https://github.com/redwoodjs/redwood/pull/6778
- https://github.com/redwoodjs/redwood
- https://github.com/redwoodjs/redwood/releases/tag/v2.2.5
- https://github.com/redwoodjs/redwood/releases/tag/v3.3.1
