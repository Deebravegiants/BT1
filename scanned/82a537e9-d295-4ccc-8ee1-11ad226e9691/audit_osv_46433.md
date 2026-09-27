# [H] CVE-2010-3844

## Summary
Severity: High
Advisory: CVE-2010-3844
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-12
Source: https://osv.dev/vulnerability/CVE-2010-3844
Type: osv

## Details
An unchecked sscanf() call in ettercap before 0.7.5 allows an insecure temporary settings file to overflow a static-sized buffer on the stack.

## References
- https://access.redhat.com/security/cve/cve-2010-3844
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=600130
- https://security-tracker.debian.org/tracker/CVE-2010-3844
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=600130
- https://github.com/Ettercap/ettercap/commit/4ef3ede30181eca9add74305ad26dbcb0c3686a0
- https://access.redhat.com/security/cve/cve-2010-3844
