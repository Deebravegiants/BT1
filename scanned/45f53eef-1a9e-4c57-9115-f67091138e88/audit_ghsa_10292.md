# [H] Directus: Authenticated Users Can Extract Concealed Fields via Aggregate Queries

## Summary
Severity: High
Advisory: GHSA-38hg-ww64-rrwc
CVE: CVE-2026-35442
CWE: CWE-200, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-38hg-ww64-rrwc
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.17.0

## Details
### Summary

Aggregate functions (`min`, `max`) applied to fields with the `conceal` special type incorrectly return raw database values instead of the masked placeholder. When combined with `groupBy`, any authenticated user with read access to the affected collection can extract concealed field values, including static API tokens and two-factor authentication secrets from `directus_users`.

### Details

Fields marked with `conceal` are protected by payload processing logic that replaces real values with a masked placeholder on read. This protection works correctly for standard item queries, but aggregate query results are structured differently, operations are nested under their function name rather than appearing as flat field keys. The masking logic does not account for this nested structure, causing it to silently skip concealed fields in aggregate responses and return their raw values to the client.

### Impact

- **Account Takeover** An authenticated attacker can harvest static API tokens for all users, including administrators, enabling immediate authentication as any account without credentials.

- **2FA Bypass** TOTP seeds stored in directus_users can similarly be extracted, allowing an attacker to bypass two-factor authentication for any account.

## References
- https://github.com/directus/directus/security/advisories/GHSA-38hg-ww64-rrwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-35442
- https://github.com/directus/directus
