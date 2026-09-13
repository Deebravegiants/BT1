# [H] Mautic has SQL Injection in API Contact Filtering

## Summary
Severity: High
Advisory: GHSA-fcmw-wx57-9p75
CVE: CVE-2026-4776
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-fcmw-wx57-9p75
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=2.6.0
- Packagist: `mautic/core` — affected >=5.0.0 <5.2.11
- Packagist: `mautic/core` — affected >=6.0.0 <6.0.9
- Packagist: `mautic/core` — affected >=7.0.0 <7.1.2

## Details
### Summary
An SQL injection vulnerability exists in Mautic's API contact filtering mechanism. Due to insufficient recursive sanitization of nested query parameters, an authenticated API user can bypass input filtering and inject arbitrary SQL commands.

### Impact
An authenticated user with API access can exploit this vulnerability to execute arbitrary SQL queries against the underlying database. This allows unauthorized retrieval of sensitive database contents—including user credentials, system configurations, and personal identifiable information (PII) of contacts—bypassing standard data access permissions.

### Patched Versions
This security issue has been fixed in the following releases:
* **7.1.2**
* **6.0.9**
* **5.2.11**
* **4.4.20** [ELTS](https://mautic.org/extended-long-term-support-elts/)

We strongly recommend upgrading to the latest version corresponding to your release branch.

### Workarounds
There are no official workarounds. To mitigate this issue without upgrading, you may temporarily disable API access or restrict API permissions to highly trusted accounts.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-fcmw-wx57-9p75
- https://nvd.nist.gov/vuln/detail/CVE-2026-4776
- https://github.com/mautic/mautic
