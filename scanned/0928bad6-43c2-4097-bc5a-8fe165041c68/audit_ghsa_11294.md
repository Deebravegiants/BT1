# [H] Cockpit CMS has SQL Injection in MongoLite Aggregation Optimizer via toJsonExtractRaw() 

## Summary
Severity: High
Advisory: GHSA-7x5c-vfhj-9628
CVE: CVE-2026-31891
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-7x5c-vfhj-9628
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.13.5

## Details
### Impact

This is a SQL Injection vulnerability in the MongoLite Aggregation Optimizer.

Any Cockpit CMS instance running version **2.13.4 or earlier** with API access enabled
is potentially affected.

**Who is impacted:**
- Any deployment where the `/api/content/aggregate/{model}` endpoint is publicly
  accessible or reachable by untrusted users.
- Attackers in possession of a **valid read-only API key** (the lowest privilege level)
  can exploit this vulnerability — no admin access is required.

**What an attacker can do:**
- Inject arbitrary SQL via unsanitized field names in aggregation queries.
- Bypass the `_state=1` published-content filter to access unpublished or restricted content.
- Extract unauthorized data from the underlying SQLite content database.

**Confidentiality impact is High.** Integrity and availability are not directly affected
by this vulnerability.

### Patches

This vulnerability has been **patched in version 2.13.5**.

All users running Cockpit CMS version **2.13.4 or earlier** are strongly advised to
upgrade to **2.13.5 or later** immediately.

- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.13.5

The fix applies the same field-name sanitization introduced in v2.13.3 for `toJsonPath()`
to the `toJsonExtractRaw()` method in `lib/MongoLite/Aggregation/Optimizer.php`,
closing the injection vector in the Aggregation Optimizer.

## References
- https://github.com/Cockpit-HQ/Cockpit/security/advisories/GHSA-7x5c-vfhj-9628
- https://nvd.nist.gov/vuln/detail/CVE-2026-31891
- https://github.com/Cockpit-HQ/Cockpit
- https://github.com/Cockpit-HQ/Cockpit/releases/tag/2.13.5
