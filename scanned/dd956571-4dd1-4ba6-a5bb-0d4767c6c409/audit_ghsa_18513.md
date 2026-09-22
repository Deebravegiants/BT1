# [H] @clerk/backend Performs Insufficient Verification of Data Authenticity

## Summary
Severity: High
Advisory: GHSA-9mp4-77wg-rwx9
CVE: CVE-2025-53548
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-9mp4-77wg-rwx9
Type: github-advisory

## Affected
- npm: `@clerk/backend` — affected >=2.0.0 <2.4.0
- npm: `@clerk/astro` — affected >=2.9.0 <2.10.2
- npm: `@clerk/express` — affected >=1.6.0 <1.7.4
- npm: `@clerk/fastify` — affected >=2.3.0 <2.4.4
- npm: `@clerk/nextjs` — affected >=6.2.10 <6.23.3
- npm: `@clerk/nuxt` — affected >=1.7.0 <1.7.5
- npm: `@clerk/react-router` — affected >=1.5.0 <1.6.4
- npm: `@clerk/remix` — affected >=4.8.0 <4.8.5
- npm: `@clerk/tanstack-react-start` — affected >=0.16.0 <0.18.3

## Details
### Impact

Applications that use the `verifyWebhook()` helper to verify incoming Clerk webhooks are susceptible to accepting improperly signed webhook events.

### Patches

* `@clerk/backend`: the helper has been patched as of `2.4.0`
* `@clerk/astro`: the helper has been patched as of `2.10.2`
* `@clerk/express`: the helper has been patched as of `1.7.4`
* `@clerk/fastify`: the helper has been patched as of `2.4.4`
* `@clerk/nextjs`: the helper has been patched as of `6.23.3`
* `@clerk/nuxt`: the helper has been patched as of `1.7.5`
* `@clerk/react-router`: the helper has been patched as of `1.6.4`
* `@clerk/remix`: the helper has been patched as of `4.8.5`
* `@clerk/tanstack-react-start`: the helper has been patched as of `0.18.3`

### Resolution

The issue was resolved in **`@clerk/backend` `2.4.0`** by:

* Properly parsing the webhook request's signatures and comparing them against the signature generated from the received event

### Workarounds

If unable to upgrade, developers can workaround this issue by verifying webhooks manually, per [this documentation](https://clerk.com/docs/webhooks/overview#protect-your-webhooks-from-abuse).

## References
- https://github.com/clerk/javascript/security/advisories/GHSA-9mp4-77wg-rwx9
- https://nvd.nist.gov/vuln/detail/CVE-2025-53548
- https://github.com/clerk/javascript
