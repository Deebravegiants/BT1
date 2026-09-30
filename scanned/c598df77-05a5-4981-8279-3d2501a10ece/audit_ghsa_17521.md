# [H] pgjdbc Client Allows Fallback to Insecure Authentication Despite channelBinding=require Configuration

## Summary
Severity: High
Advisory: GHSA-hq9p-pm7w-8p54
CVE: CVE-2025-49146
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-06-11
Source: https://github.com/advisories/GHSA-hq9p-pm7w-8p54
Type: github-advisory

## Affected
- Maven: `org.postgresql:postgresql` — affected >=42.7.4 <42.7.7

## Details
### Impact
When the PostgreSQL JDBC driver is configured with channel binding set to `required` (default value is `prefer`), the driver would incorrectly allow connections to proceed with authentication methods that do not support channel binding (such as password, MD5, GSS, or SSPI  authentication). This could allow a man-in-the-middle attacker to intercept connections that users believed were protected by channel binding requirements.

### Patches
TBD

### Workarounds

Configure `sslMode=verify-full` to prevent MITM attacks.

### References

* https://www.postgresql.org/docs/current/sasl-authentication.html#SASL-SCRAM-SHA-256
* https://datatracker.ietf.org/doc/html/rfc7677
* https://datatracker.ietf.org/doc/html/rfc5802

## References
- https://github.com/pgjdbc/pgjdbc/security/advisories/GHSA-hq9p-pm7w-8p54
- https://nvd.nist.gov/vuln/detail/CVE-2025-49146
- https://github.com/pgjdbc/pgjdbc/commit/9217ed16cb2918ab1b6b9258ae97e6ede244d8a0
- https://datatracker.ietf.org/doc/html/rfc5802
- https://datatracker.ietf.org/doc/html/rfc7677
- https://github.com/pgjdbc/pgjdbc
- https://www.postgresql.org/docs/current/sasl-authentication.html#SASL-SCRAM-SHA-256
