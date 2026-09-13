# [H] CVE-2014-8184

## Summary
Severity: High
Advisory: CVE-2014-8184
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2014-8184
Type: osv

## Details
A vulnerability was found in liblouis, versions 2.5.x before 2.5.4. A stack-based buffer overflow was found in findTable() in liblouis. An attacker could create a malicious file that would cause applications that use liblouis (such as Orca) to crash, or potentially execute arbitrary code when opened.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-8184
- https://github.com/liblouis/liblouis/issues/425
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-8184
- https://github.com/liblouis/liblouis/issues/425
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-8184
- https://github.com/liblouis/liblouis/issues/425
