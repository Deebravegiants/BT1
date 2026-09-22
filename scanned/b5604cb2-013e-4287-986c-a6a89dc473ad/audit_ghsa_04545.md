# [H] Better Auth: Device authorization approve and deny accept any authenticated session while the user code is pending

## Summary
Severity: High
Advisory: GHSA-cq3f-vc6p-68fh
CVE: CVE-2026-45337
CWE: CWE-285, CWE-345, CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-cq3f-vc6p-68fh
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=1.6.0 <1.6.11

## Details
### Am I affected?

You are affected if all of the following are true:

- You use `better-auth` at a version `>= 1.6.0, < 1.6.11`.
- The `deviceAuthorization` plugin is enabled in your auth config (`deviceAuthorization()` in your `plugins` array).
- A third party can observe a pending user code before the legitimate user completes verification.

The standard device-flow UX displays user codes to humans, so realistic exposure includes shoulder-surfing, screen-share, voice or video calls, support-chat transcripts, referrer headers, and shared logs.

If your application does not enable the `deviceAuthorization` plugin, you are not affected.

Fix:

1. Upgrade to `better-auth@1.6.11` or later.
2. If you cannot upgrade, see workarounds below.

### Summary

Better Auth's `deviceAuthorization` plugin treated any authenticated session as the owner of any pending device code. The ownership gate on `POST /device/approve` and `POST /device/deny` short-circuited whenever the row's `userId` was unset, and the `GET /device` verification handler did not claim the row. An authenticated attacker who learned a valid `user_code` before the legitimate user completed approval could bind the polling device to the attacker's account or deny the legitimate flow.

### Details

The device authorization flow binds the polling device to the user who entered the user code on the verification page. In affected versions, the plugin only created that binding at approve or deny time, with no claim at the verification step. The ownership check at approve and deny short-circuited when the owner was missing, accepting any authenticated caller instead of rejecting the request.

The fix changes `GET /device` to claim the pending row for the calling session. The approve and deny gates now require strict equality between the row's owner and the calling session. RFC 8628 §5.5 covers this risk class as Session Spying: a malicious party can hijack a session by completing authorization before the legitimate initiating user does.

### Patches

Fixed in `better-auth@1.6.11`. After the patch, `GET /device` claims the pending row for the calling session, and `POST /device/approve` and `POST /device/deny` reject calls whose session does not match the claimed owner. Custom verification pages must serve `GET /device` to an authenticated session for the flow to succeed.

### Workarounds

If you cannot upgrade immediately:

- **Disable the plugin** if you do not use the device flow: remove `deviceAuthorization()` from your `plugins` array.
- **Add a `before` hook** on `POST /device/approve` and `POST /device/deny` that tracks which session called `GET /device` for each user code, and rejects calls from a different session.
- **Shorten the pending lifetime of device codes** via the `expiresIn` plugin option to reduce the exploitation window.

### Impact

- **Account takeover on the polling device**: the attacker's session becomes the device's session, so the device operates as the attacker.
- **Denial of the legitimate sign-in**: the attacker can mark the code as denied, blocking the victim's flow.

### Credit

Reported by Quikturn Security Team.

### References

- [CWE-285: Improper Authorization](https://cwe.mitre.org/data/definitions/285.html)
- [CWE-863: Incorrect Authorization](https://cwe.mitre.org/data/definitions/863.html)
- [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)
- [RFC 8628 §5.5: Session Spying](https://datatracker.ietf.org/doc/html/rfc8628#section-5.5)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-cq3f-vc6p-68fh
- https://github.com/better-auth/better-auth/pull/9573
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
