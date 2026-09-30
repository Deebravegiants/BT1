# [H] Apache Log4j 1.x (EOL) allows Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-vp98-w2p3-mv35
CVE: CVE-2023-26464
CWE: CWE-400, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-vp98-w2p3-mv35
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=1.0.4 <2.0
- Maven: `log4j:log4j` — affected >=1.0.4 <2.0

## Details
** UNSUPPORTED WHEN ASSIGNED ** When using the Chainsaw or SocketAppender components with Log4j 1.x on JRE less than 1.7, an attacker that manages to cause a logging entry involving a specially-crafted (ie deeply nested) hashmap or hashtable (depending on which logging component is in use) to be processed could exhaust the available memory in the virtual machine and achieve Denial of Service when the object is deserialized. This issue affects Apache Log4j before 2. Affected users are recommended to update to Log4j 2.x. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26464
- https://github.com/apache/logging-log4j2
- https://lists.apache.org/thread/wkx6grrcjkh86crr49p4blc1v1nflj3t
- https://security.netapp.com/advisory/ntap-20230505-0008
