# [M] Password Pusher Allows Session Token Interception Leading to Potential Hijacking

## Summary
Severity: Medium
Advisory: GHSA-4fwj-m62q-pp47
CVE: CVE-2024-56733
CWE: CWE-384
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-30
Source: https://github.com/advisories/GHSA-4fwj-m62q-pp47
Type: github-advisory

## Affected
- RubyGems: `pwpush` — affected >=0

## Details
### Impact

A vulnerability has been reported in Password Pusher where an attacker can copy the session cookie before a user logs out, potentially allowing session hijacking.

Although the session token is replaced and invalidated upon logout, if an attacker manages to capture the session cookie before this process, they can use the token to gain unauthorized access to the user's session until the token expires or is manually cleared.

This vulnerability hinges on the attacker's ability to access the session cookie during an active session, either through a man-in-the-middle attack, by exploiting another vulnerability like XSS, or via direct access to the victim's device.

### Patches

Although there is no direct resolution to this vulnerability, it is recommended to always use the latest version of Password Pusher to best mitigate risk.

### Workarounds

If self-hosting, ensure Password Pusher is hosted exclusively over SSL connections to encrypt traffic and prevent session cookies from being intercepted in transit. Additionally, implement best practices in local security to safeguard user systems, browsers, and data against unauthorized access.

To further mitigate session hijacking risks, Password Pusher implements the following security measures:

1. **Automatic Session Expiration**: Sessions are automatically expired after 2 hours of inactivity, reducing the window for potential exploitation.
2. **Session Reset on Login and Logout**: Sessions are fully reset both when a user logs in and logs out, ensuring that session tokens are not reusable post-logout. This practice invalidates old session tokens and issues new ones, minimizing the risk of session hijacking.
3. **Encrypted Cookies**: Cookies are encrypted using the value of SECRET_KEY_BASE from the application's configuration. This encryption adds a layer of protection against tampering or reading the session cookie's contents if intercepted, although it doesn't prevent the cookie from being used if stolen.

**Note**: While these measures significantly enhance security, they are part of a broader security strategy.

### References

* https://edgeguides.rubyonrails.org/security.html#session-hijacking

### Credits

Thank you to [Positive Technologies](https://www.ptsecurity.com/ww-en/) for reporting and working with me to bring this CVE to the community.

## References
- https://github.com/pglombardo/PasswordPusher/security/advisories/GHSA-4fwj-m62q-pp47
- https://nvd.nist.gov/vuln/detail/CVE-2024-56733
- https://github.com/pglombardo/PasswordPusher
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pwpush/CVE-2024-56733.yml
