# [H] CocoIndex Doris target connector didn't verify table name when constructing ALTER TABLE statements

## Summary
Severity: High
Advisory: GHSA-59g6-v3vg-f7wc
CVE: CVE-2026-28438
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-59g6-v3vg-f7wc
Type: github-advisory

## Affected
- PyPI: `cocoindex` — affected >=0 <0.3.34

## Details
### Impact
The Doris target connector didn't verify the configured table name before creating some SQL statements (`ALTER TABLE`). So, in the application code, if the table name is provided by an untrusted upstream, it expose vulnerability to SQL injection when target schema change.

### Patches
Yes, it's fixed in cocoindex 0.3.34: we start to validate table names passed to Doris target at entry point and error out immediately if it's not a valid identifier.

### Workarounds
Users should make sure table names used to configure CocoIndex targets are valid, regardless of this fix. Which means

- The table name comes from a trusted source (e.g. for most cases it's just a fixed string literal).
- Even if it comes from an untrusted source (e.g. provided by end user), it should be validated before using it to configure the Doris target for CocoIndex.

## References
- https://github.com/cocoindex-io/cocoindex/security/advisories/GHSA-59g6-v3vg-f7wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-28438
- https://github.com/cocoindex-io/cocoindex/commit/ba2fc4a89e22d35572c64bd2990737c7913b0729
- https://github.com/cocoindex-io/cocoindex
