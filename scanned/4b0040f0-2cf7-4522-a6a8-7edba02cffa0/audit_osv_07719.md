# [C] Apache Tomcat: console manipulation via escape sequences in log messages

## Summary
Severity: Critical
Advisory: BIT-tomcat-2025-55754
Aliases: CVE-2025-55754, GHSA-vfww-5hm6-hx2j
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-tomcat-2025-55754
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.11

## Details
Improper Neutralization of Escape, Meta, or Control Sequences vulnerability in Apache Tomcat.

Tomcat did not escape ANSI escape sequences in log messages. If Tomcat was running in a console on a Windows operating system, and the console supported ANSI escape sequences, it was possible for an attacker to use a specially crafted URL to inject ANSI escape sequences to manipulate the console and the clipboard and attempt to trick an administrator into running an attacker controlled command. While no attack vector was found, it may have been possible to mount this attack on other operating systems.



This issue affects Apache Tomcat: from 11.0.0 through 11.0.10, from 10.1.0 through 10.1.44, from 9.0.40 through 9.0.108.

The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.60 though 8.5.100. Other, older, EOL versions may also be affected.
Users are recommended to upgrade to version 11.0.11 or later, 10.1.45 or later or 9.0.109 or later, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/10/27/5
- https://lists.apache.org/thread/j7w54hqbkfcn0xb9xy0wnx8w5nymcbqd
- https://nvd.nist.gov/vuln/detail/CVE-2025-55754
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
