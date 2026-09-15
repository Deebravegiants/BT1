# [H] Potential CSV export data leak

## Summary
Severity: High
Advisory: GHSA-356j-hg45-x525
CVE: CVE-2023-50448
CWE: CWE-1236, CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-356j-hg45-x525
Type: github-advisory

## Affected
- RubyGems: `activeadmin` — affected >=0 <2.12.0

## Details
### Impact

In ActiveAdmin versions prior to 2.12.0, a concurrency issue was found that could allow a malicious actor to be able to access potentially private data that belongs to another user.

The bug affects the functionality to export data as CSV files, and was caused by a variable holding the collection to be exported being shared across threads and not properly synchronized.

The attacker would need access to the same ActiveAdmin application as the victim, and could exploit the issue by timing their request immediately before when they know someone else will request a CSV (e.g. via phishing) or request CSVs frequently and hope someone else makes a concurrent request.

### Patches

Versions 2.12.0 and above fixed the problem by completely removing the shared state.

## References
- https://github.com/activeadmin/activeadmin/security/advisories/GHSA-356j-hg45-x525
- https://nvd.nist.gov/vuln/detail/CVE-2023-50448
- https://github.com/activeadmin/activeadmin/pull/7336
- https://github.com/activeadmin/activeadmin
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activeadmin/CVE-2023-50448.yml
