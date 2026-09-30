# [H] sqlite vulnerable to code execution due to Object coercion

## Summary
Severity: High
Advisory: GHSA-jqv5-7xpx-qj74
CVE: CVE-2022-43441
CWE: CWE-913, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-jqv5-7xpx-qj74
Type: github-advisory

## Affected
- npm: `sqlite3` — affected >=5.0.0 <5.1.5

## Details
### Impact

Due to the underlying implementation of `.ToString()`, it's possible to execute arbitrary JavaScript, or to achieve a denial-of-service, if a binding parameter is a crafted Object.

Users of `sqlite3` v5.0.0 - v5.1.4 are affected by this.

### Patches

Fixed in v5.1.5. All users are recommended to upgrade to v5.1.5 or later.

### Workarounds

* Ensure there is sufficient sanitization in the parent application to protect against invalid values being supplied to binding parameters.

### References

* Commit: https://github.com/TryGhost/node-sqlite3/commit/edb1934dd222ae55632e120d8f64552d5191c781

### For more information

If you have any questions or comments about this advisory:

* Email us at [security@ghost.org](mailto:security@ghost.org)

Credits: Dave McDaniel of Cisco Talos

## References
- https://github.com/TryGhost/node-sqlite3/security/advisories/GHSA-jqv5-7xpx-qj74
- https://nvd.nist.gov/vuln/detail/CVE-2022-43441
- https://github.com/TryGhost/node-sqlite3/commit/edb1934dd222ae55632e120d8f64552d5191c781
- https://github.com/TryGhost/node-sqlite3
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1645
