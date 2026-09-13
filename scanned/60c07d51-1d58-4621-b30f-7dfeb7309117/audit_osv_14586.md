# [H] CVE-2019-10181

## Summary
Severity: High
Advisory: CVE-2019-10181
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-10181
Type: osv

## Details
It was found that in icedtea-web up to and including 1.7.2 and 1.8.2 executable code could be injected in a JAR file without compromising the signature verification. An attacker could use this flaw to inject code in a trusted JAR. The code would be executed inside the sandbox.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00045.html
- http://packetstormsecurity.com/files/154748/IcedTeaWeb-Validation-Bypass-Directory-Traversal-Code-Execution.html
- https://github.com/AdoptOpenJDK/IcedTea-Web/issues/327
- https://lists.debian.org/debian-lts-announce/2019/09/msg00008.html
- https://seclists.org/bugtraq/2019/Oct/5
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10181
- https://github.com/AdoptOpenJDK/IcedTea-Web/pull/344
- https://security.gentoo.org/glsa/202107-51
