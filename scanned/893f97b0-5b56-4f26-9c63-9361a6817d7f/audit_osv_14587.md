# [M] CVE-2019-10182

## Summary
Severity: Medium
Advisory: CVE-2019-10182
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-10182
Type: osv

## Details
It was found that icedtea-web though 1.7.2 and 1.8.2 did not properly sanitize paths from <jar/> elements in JNLP files. An attacker could trick a victim into running a specially crafted application and use this flaw to upload arbitrary files to arbitrary locations in the context of the user.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00045.html
- http://packetstormsecurity.com/files/154748/IcedTeaWeb-Validation-Bypass-Directory-Traversal-Code-Execution.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00008.html
- https://seclists.org/bugtraq/2019/Oct/5
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10182
- https://github.com/AdoptOpenJDK/IcedTea-Web/issues/327
- https://github.com/AdoptOpenJDK/IcedTea-Web/pull/344
