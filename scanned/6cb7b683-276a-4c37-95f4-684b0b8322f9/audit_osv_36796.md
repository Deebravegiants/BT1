# [H] Hollo DMs get leaked and can be seen on Webfinger Browser

## Summary
Severity: High
Advisory: CVE-2026-25808
Aliases: GHSA-6r2w-3pcj-v4v5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25808
Type: osv

## Details
Hollo is a federated single-user microblogging software designed to be federated through ActivityPub. Prior to 0.6.20 and 0.7.2, there is a security vulnerability where DMs and followers-only posts were exposed through the ActivityPub outbox endpoint without authorization. This vulnerability is fixed in 0.6.20 and 0.7.2.

## References
- https://github.com/fedify-dev/hollo/releases/tag/0.6.20
- https://github.com/fedify-dev/hollo/releases/tag/0.7.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25808.json
- https://github.com/fedify-dev/hollo/security/advisories/GHSA-6r2w-3pcj-v4v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25808
- https://github.com/fedify-dev/hollo/commit/329969c502ef092d5c3f9c2c20421c34f4ff0f0e
