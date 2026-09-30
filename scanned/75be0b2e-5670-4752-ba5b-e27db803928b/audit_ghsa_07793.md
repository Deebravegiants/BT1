# [C] Ghost has a SQL injection in Content API

## Summary
Severity: Critical
Advisory: GHSA-w52v-v783-gw97
CVE: CVE-2026-26980
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-w52v-v783-gw97
Type: github-advisory

## Affected
- npm: `ghost` — affected >=3.24.0 <6.19.1

## Details
### Impact

A SQL injection vulnerability existed in Ghost's Content API that allowed unauthenticated attackers to read arbitrary data from the database. 

### Vulnerable Versions

This vulnerability is present in Ghost v3.24.0 to v6.19.0.

### Patches

v6.19.1 contains a fix for this issue. 

**Note:** as this vulnerability lets an attacker gain access to a site's API keys, we recommend reviewing staff users and rotating keys. We generally recommend always updating Ghost to its most current version. 

### Workarounds

There is no application-level workaround. The Content API key is public by design, so restricting key access does not mitigate this vulnerability.

As a temporary mitigation, a reverse proxy or WAF rule can be used to block Content API requests containing `slug%3A%5B` or `slug:[` in the query string filter parameter. Note that this may break legitimate slug filter functionality.

### References

We thank Nicholas Carlini using Claude, Anthropic for disclosing this vulnerability responsibly. 

### For more information
If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-w52v-v783-gw97
- https://nvd.nist.gov/vuln/detail/CVE-2026-26980
- https://github.com/TryGhost/Ghost/commit/30868d632b2252b638bc8a4c8ebf73964592ed91
- https://blog.xlab.qianxin.com/ghost-cms-page-poisoning-cve-2026-26980
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.19.1
