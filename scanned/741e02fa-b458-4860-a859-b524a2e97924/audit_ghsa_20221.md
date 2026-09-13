# [H] TiDB authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-4whx-7p29-mq22
CVE: CVE-2022-31011
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-06
Source: https://github.com/advisories/GHSA-4whx-7p29-mq22
Type: github-advisory

## Affected
- Go: `github.com/pingcap/tidb` — affected >=5.3.0 <5.3.1
- Go: `github.com/pingcap/tidb` — affected >=0.0.0-20210808221113-a7fdc2a05663 <0.0.0-20220221072141-27ffd1126da1
- Go: `github.com/pingcap/tidb` — affected >=1.1.0-beta.0.20210808221113-a7fdc2a05663 <1.1.0-beta.0.20220221072141-27ffd1126da1

## Details
### Impact
Under certain conditions, an attacker can construct malicious authentication requests to bypass the authentication process, resulting in privilege escalation or unauthorized access.
Only users using TiDB 5.3.0 are affected by this vulnerability.

### Patches
Please upgrade to TiDB 5.3.1 or higher version

### Workarounds
You can also mitigate risks by taking the following measures.
Option 1: Turn off SEM (Security Enhanced Mode).
Option 2: Disable local login for non-root accounts and ensure that the same IP cannot be logged in as root or normal user at the same time.

### References
https://en.pingcap.com/download/

### For more information
If you have any questions or comments about this advisory:
* Email us at security@tidb.io

## References
- https://github.com/pingcap/tidb/security/advisories/GHSA-4whx-7p29-mq22
- https://nvd.nist.gov/vuln/detail/CVE-2022-31011
- https://github.com/pingcap/tidb
- https://github.com/pingcap/tidb/releases/tag/v5.3.1
