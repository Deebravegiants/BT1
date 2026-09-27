# [C] Apache IoTDB: Authentication Bypass via Forged SessionID in Thrift RPC

## Summary
Severity: Critical
Advisory: CVE-2026-24013
Aliases: PYSEC-2026-2080
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-24013
Type: osv

## Details
Authentication Bypass by Spoofing vulnerability in Apache IoTDB.
Certain Thrift RPC query handlers lack strict validation of the sessionId
parameter. An attacker can construct requests with a forged sessionId and,
without performing openSession authentication, receive valid query results.
This allows authentication bypass and unauthorized reading of time-series
data.


This issue affects Apache IoTDB: from 1.3.3 before 2.0.8.

Users are recommended to upgrade to version 2.0.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24013.json
- https://lists.apache.org/thread/6pwkgnqhbm56mvn309f87snm84s0b75y
- https://nvd.nist.gov/vuln/detail/CVE-2026-24013
