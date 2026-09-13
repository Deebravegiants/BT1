# [M] Infinite Loop in Apache James

## Summary
Severity: Medium
Advisory: GHSA-fqgw-6qj5-8hmp
CVE: CVE-2021-40111
CWE: CWE-835
Ecosystem: Maven
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-fqgw-6qj5-8hmp
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0 <3.6.1

## Details
In Apache James, while fuzzing with Jazzer the IMAP parsing stack, we discover that crafted APPEND and STATUS IMAP command could be used to trigger infinite loops resulting in expensive CPU computations and OutOfMemory exceptions. This can be used for a Denial Of Service attack. The IMAP user needs to be authenticated to exploit this vulnerability. This affected Apache James prior to version 3.6.1. This vulnerability had been patched in Apache James 3.6.1 and higher. We recommend the upgrade.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40111
- https://www.openwall.com/lists/oss-security/2022/01/04/3
- http://www.openwall.com/lists/oss-security/2022/01/04/3
