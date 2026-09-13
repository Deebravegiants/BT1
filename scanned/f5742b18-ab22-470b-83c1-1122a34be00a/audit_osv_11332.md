# [H] CVE-2017-7435

## Summary
Severity: High
Advisory: CVE-2017-7435
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-7435
Type: osv

## Details
In libzypp before 20170803 it was possible to add unsigned YUM repositories without warning to the user that could lead to man in the middle or malicious servers to inject malicious RPM packages into a users system.

## References
- https://lists.opensuse.org/opensuse-security-announce/2017-08/msg00002.html
- https://www.suse.com/de-de/security/cve/CVE-2017-7435/
- https://bugzilla.suse.com/show_bug.cgi?id=1009127
