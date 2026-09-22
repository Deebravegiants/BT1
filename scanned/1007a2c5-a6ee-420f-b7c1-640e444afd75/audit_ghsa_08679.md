# [H] HAX open-apis: Credential Theft via Server-Side Request Forgery (SSRF) in open-apis

## Summary
Severity: High
Advisory: GHSA-4fg7-f244-3j49
CVE: CVE-2026-46391
CWE: CWE-183, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-4fg7-f244-3j49
Type: github-advisory

## Affected
- npm: `@haxtheweb/open-apis` — affected >=0 <26.0.0

## Details
### Summary
Multiple functions conduct substring-only matching to validate hostnames to which basic authorization should be sent. An attacker can append the matched substrings to an attacker-controlled endpoint and capture authentication.

### Details
[api/services/website/cacheAddress.js](https://github.com/haxtheweb/open-apis/blob/ff694ce91442c39ae1a78dc21e9ce50546aa207a/api/services/website/cacheAddress.js#L21), [api/apps/haxcms/lib/JOSHelpers.js](https://github.com/haxtheweb/open-apis/blob/ff694ce91442c39ae1a78dc21e9ce50546aa207a/api/apps/haxcms/lib/JOSHelpers.js#L26), and [api/apps/haxcms/convert/elmslnToSite.js](https://github.com/haxtheweb/open-apis/blob/ff694ce91442c39ae1a78dc21e9ce50546aa207a/api/apps/haxcms/convert/elmslnToSite.js#L37) use similar logic to check for hard-coded site names. However, the logic only looks for the substring to be included in the user-controlled string, allowing an attacker to craft an API call and extract the credentials intended for the hard-coded domains.

### PoC
Making API calls to an affected endpoint will result in credential theft. The attacker-controlled domains in these proofs of concept are `cloudflared` tunnels, protecting the production credentials from unencrypted exposure.

cacheAddress.js:
<img width="3404" height="1656" alt="ssrf_cred_theft" src="https://github.com/user-attachments/assets/0a87cef5-3c4d-450a-8bb7-35123d5f621b" />

elmslnToSite.js:
<img width="3409" height="1641" alt="theft2" src="https://github.com/user-attachments/assets/bede82cc-a613-4fc7-bbf6-76166af784f5" />

JOSHelpers.js:
<img width="3407" height="1597" alt="theft3" src="https://github.com/user-attachments/assets/4f3f8bee-443e-4b22-9d41-eb9726619d36" />

### Impact
This vulnerability allows internal data, including secrets, to be exfiltrated to an attacker-controlled domain. Credentials were confirmed with the maintainer to grant access to unreleased LMS content on subsequent systems; out of scope for PoC.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-4fg7-f244-3j49
- https://nvd.nist.gov/vuln/detail/CVE-2026-46391
- https://github.com/haxtheweb/issues
