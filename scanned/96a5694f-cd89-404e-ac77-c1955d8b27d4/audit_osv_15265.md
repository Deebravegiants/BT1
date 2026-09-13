# [H] CVE-2019-14868

## Summary
Severity: High
Advisory: CVE-2019-14868
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-02
Source: https://osv.dev/vulnerability/CVE-2019-14868
Type: osv

## Details
In ksh version 20120801, a flaw was found in the way it evaluates certain environment variables. An attacker could use this flaw to override or bypass environment restrictions to execute shell commands. Services and applications that allow remote unauthenticated attackers to provide one of those environment variables could allow them to exploit this issue remotely.

## References
- http://seclists.org/fulldisclosure/2020/May/53
- https://lists.debian.org/debian-lts-announce/2020/07/msg00015.html
- https://support.apple.com/kb/HT211170
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14868
- https://github.com/att/ast/commit/c7de8b641266bac7c77942239ac659edfee9ecd2
