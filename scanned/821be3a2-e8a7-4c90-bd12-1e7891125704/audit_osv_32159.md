# [M] Apache Kvrocks: Cross-Protocol Scripting Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-25069
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-02-07
Source: https://osv.dev/vulnerability/CVE-2025-25069
Type: osv

## Details
A Cross-Protocol Scripting vulnerability is found in Apache Kvrocks.

Since Kvrocks didn't detect if "Host:" or "POST" appears in RESP requests,
a valid HTTP request can also be sent to Kvrocks as a valid RESP request 
and trigger some database operations, which can be dangerous when 
it is chained with SSRF.

It is similiar to CVE-2016-10517 in Redis.

This issue affects Apache Kvrocks: from the initial version to the latest version 2.11.0.

Users are recommended to upgrade to version 2.11.1, which fixes the issue.

## References
- https://www.cve.org/CVERecord?id=CVE-2016-10517
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25069.json
- https://lists.apache.org/thread/gbxv9gpsskmdzg6z48zm3tvo8cyo9v3t
- https://nvd.nist.gov/vuln/detail/CVE-2025-25069
