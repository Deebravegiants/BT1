# [M] Flarum notifications can leak restricted content

## Summary
Severity: Medium
Advisory: GHSA-8gcg-vwmw-rxj4
CVE: CVE-2023-22488
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-8gcg-vwmw-rxj4
Type: github-advisory

## Affected
- Packagist: `flarum/core` — affected >=0 <1.6.3

## Details
Using the notifications feature, one can read restricted/private content and bypass access checks that would be in place for such content.

The notification-sending component does not check that the subject of the notification can be seen by the receiver, and proceeds to send notifications through their different channels. The alerts do not leak data despite this as they are listed based on a visibility check, however, emails are still sent out.

This means that, for extensions which restrict access to posts, any actor can bypass the restriction by subscribing to the discussion if the [*Subscriptions*](https://extiverse.com/extension/flarum/subscriptions) extension is enabled.

### Impact
The attack allows the leaking of some posts in the forum database, including posts awaiting approval, posts in tags the user has no access to if they could subscribe to a discussion before it becomes private, and posts restricted by third-party extensions.

Other leaks could also happen for different notification subjects if some features allowed to receive specific types of notifications for restricted content.

All Flarum versions prior to v1.6.3 are affected.

### Patches
The vulnerability has been fixed and published as flarum/core v1.6.3. All communities running Flarum should upgrade as soon as possible to v1.6.3 using:

```
composer update --prefer-dist --no-dev -a -W
```
You can then confirm you run the latest version using:

```
composer show flarum/core
```

### Workarounds
Disable the Flarum Subscriptions extension or disable email notifications altogether.

**There is no other supported workaround for this issue for Flarum versions below 1.6.3.**

### For more information
For any questions or comments on this vulnerability please visit https://discuss.flarum.org/

For support questions create a discussion at https://discuss.flarum.org/t/support.

A reminder that if you ever become aware of a security issue in Flarum, please report it to us privately by emailing [security@flarum.org](mailto:security@flarum.org), and we will address it promptly.

## References
- https://github.com/flarum/framework/security/advisories/GHSA-8gcg-vwmw-rxj4
- https://nvd.nist.gov/vuln/detail/CVE-2023-22488
- https://github.com/flarum/framework/commit/d0a2b95dca57d3dae9a0d77b610b1cb1d0b1766a
- https://github.com/flarum/framework
- https://github.com/flarum/framework/releases/tag/v1.6.3
