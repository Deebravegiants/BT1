# [H] CVE-2017-12628

## Summary
Severity: High
Advisory: CVE-2017-12628
Aliases: GHSA-xj7q-q94c-6wr3
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-20
Source: https://osv.dev/vulnerability/CVE-2017-12628
Type: osv

## Details
The JMX server embedded in Apache James, also used by the command line client is exposed to a java de-serialization issue, and thus can be used to execute arbitrary commands. As James exposes JMX socket by default only on local-host, this vulnerability can only be used for privilege escalation. Release 3.0.1 upgrades the incriminated library.

## References
- https://www.mail-archive.com/server-user%40james.apache.org/msg15633.html
- http://www.securityfocus.com/bid/101532
