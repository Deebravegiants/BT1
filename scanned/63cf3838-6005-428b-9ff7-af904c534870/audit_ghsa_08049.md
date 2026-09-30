# [M] Lettermint Node.js SDK leaks email properties to unintended recipients when client instance is reused

## Summary
Severity: Medium
Advisory: GHSA-49pc-8936-wvfp
CVE: CVE-2026-27492
CWE: CWE-488
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-49pc-8936-wvfp
Type: github-advisory

## Affected
- npm: `lettermint` — affected >=0 <1.5.1

## Details
### Impact
Email properties (such as to, subject, html, text, and attachments) are not reset between sends when a single client instance is reused across multiple .send() calls. This can cause properties from a previous send to leak into a subsequent one, potentially delivering content or recipient addresses to unintended parties. Applications sending emails to different recipients in sequence — such as transactional flows like password resets or notifications — are affected.

### Patches
Yes, the issue has been patched. Users should upgrade to v1.5.1 or later.

### Workarounds
If upgrading immediately is not possible, instantiate a new client for each send:
```js
const client = new Lettermint({ apiKey: process.env.LETTERMINT_API_KEY });
await client.email.to('...').subject('...').html('...').send();
```

This ensures no state is carried over between sends.

## References
- https://github.com/lettermint/lettermint-node/security/advisories/GHSA-49pc-8936-wvfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27492
- https://github.com/lettermint/lettermint-node/commit/24a17acbc2429c5eb30391f9df3dc0ea7aaf4de1
- https://github.com/lettermint/lettermint-node
- https://github.com/lettermint/lettermint-node/blob/main/CHANGELOG.md#151-2026-02-20
