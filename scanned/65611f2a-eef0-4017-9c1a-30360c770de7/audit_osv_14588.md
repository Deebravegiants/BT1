# [H] CVE-2019-10185

## Summary
Severity: High
Advisory: CVE-2019-10185
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-10185
Type: osv

## Details
It was found that icedtea-web up to and including 1.7.2 and 1.8.2 was vulnerable to a zip-slip attack during auto-extraction of a JAR file. An attacker could use this flaw to write files to arbitrary locations. This could also be used to replace the main running application and, possibly, break out of the sandbox.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00045.html
- http://packetstormsecurity.com/files/154748/IcedTeaWeb-Validation-Bypass-Directory-Traversal-Code-Execution.html
- https://github.com/AdoptOpenJDK/IcedTea-Web/issues/327
- https://lists.debian.org/debian-lts-announce/2019/09/msg00008.html
- https://seclists.org/bugtraq/2019/Oct/5
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10185
- https://github.com/AdoptOpenJDK/IcedTea-Web/pull/344
- https://security.gentoo.org/glsa/202107-51
