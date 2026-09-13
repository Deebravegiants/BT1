# [M] Graylog token revocation endpoint allows authenticated users to delete other users’ access tokens

## Summary
Severity: Medium
Advisory: GHSA-j769-9gv9-65gr
CVE: CVE-2026-55867
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-j769-9gv9-65gr
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=6.2.0 <6.3.12
- Maven: `org.graylog2:graylog2-server` — affected >=7.0.0 <7.0.7
- Maven: `org.graylog2:graylog2-server` — affected >=7.1.0 <7.1.2

## Details
### Impact

Graylog contains an insecure direct object reference (IDOR) vulnerability in the token revocation endpoint. An authenticated user can delete access tokens belonging to other users, including service account tokens and administrator tokens, if they know or can guess a valid token identifier.

The issue does not expose token contents, but it allows unauthorized token deletion, leading to integrity impact and potential availability impact for access token based integrations.

### Patches

The issue has been fixed in the following Graylog versions: `6.3.12`, `7.0.7`, `7.1.2`. Users should upgrade to one of these versions or above to remediate the vulnerability.

Graylog Cloud has already been patched.

### Workarounds

There are no feasible workarounds for this issue. Upgrading to a patched version is recommended.

Customers using Graylog Enterprise or Security can review the audit log[^1] for suspicious activity. Audit log lines for successful token deletions begin with `access token deleted from user`. 

### Credits

Thanks to [michaelddickenson](https://github.com/michaelddickenson) and [sreelim](https://github.com/sreelim) for reporting.


[^1]: https://go2docs.graylog.org/current/interacting_with_your_log_data/audit_log.html

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-j769-9gv9-65gr
- https://github.com/Graylog2/graylog2-server/pull/26049
- https://github.com/Graylog2/graylog2-server/pull/26051
- https://github.com/Graylog2/graylog2-server/pull/26053
- https://github.com/Graylog2/graylog2-server/pull/26055
- https://github.com/Graylog2/graylog2-server/commit/41d3745d0e52736d06c07d279ca0d72c1616df4c
- https://github.com/Graylog2/graylog2-server/commit/4f280138b53dc3bbb5749213e8cb1c8e372f23a2
- https://github.com/Graylog2/graylog2-server/commit/84b0ffa0bdf918f6edd2bb23a47254088634b1fc
- https://github.com/Graylog2/graylog2-server/commit/e5accc5f4ce48bd61b84bb8e5a13d21f8eac3da5
- https://github.com/Graylog2/graylog2-server
