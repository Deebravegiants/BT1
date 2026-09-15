# [M] traQ Allows Insertion of Sensitive Information into Log File

## Summary
Severity: Medium
Advisory: GHSA-27r7-3m9x-r533
CVE: CVE-2025-57813
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-27r7-3m9x-r533
Type: github-advisory

## Affected
- Go: `github.com/traPtitech/traQ` — affected >=0 <3.25.0

## Details
### Impact
A vulnerability exists where sensitive information, such as OAuth tokens, is recorded in log files when an error occurs during the execution of an SQL query.
An attacker could intentionally trigger an SQL error by methods such as placing a high load on the database. This could allow an attacker who has the authority to view the log files to illicitly acquire the recorded sensitive information.

### Patch
This vulnerability was temporarily fixed by #2787 and will be completely resolved by #2788. 

This issue may have caused OAuth tokens to be leaked to users who can view logs on traQ instances using versions prior to v3.25.0.

While it is possible that OAuth tokens for both human users and Bots were leaked, revoking Bot access tokens is not recommended as it may cause errors. This issue will be resolved in a future update.

Currently, the recommended mitigation is to invalidate the OAuth tokens of human users only. To apply this measure, please execute the following SQL statement directly:
```sql
UPDATE oauth2_tokens SET deleted_at = NOW() WHERE deleted_at IS NULL AND scopes != "bot"
```

### Workaround
If you cannot apply the update immediately, as a temporary workaround, please review access permissions for SQL error logs and strictly limit access to prevent unauthorized users from viewing them.

## References
- https://github.com/traPtitech/traQ/security/advisories/GHSA-27r7-3m9x-r533
- https://nvd.nist.gov/vuln/detail/CVE-2025-57813
- https://github.com/traPtitech/traQ/pull/2787
- https://github.com/traPtitech/traQ/pull/2788
- https://github.com/traPtitech/traQ/commit/ce5da94f5d5a8348f9ecdc82140b6f53b3721698
- https://github.com/traPtitech/traQ
- https://pkg.go.dev/vuln/GO-2025-3913
