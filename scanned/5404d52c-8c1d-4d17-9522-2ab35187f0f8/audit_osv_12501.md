# [H] CVE-2018-12550

## Summary
Severity: High
Advisory: CVE-2018-12550
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2018-12550
Type: osv

## Details
When Eclipse Mosquitto version 1.0 to 1.5.5 (inclusive) is configured to use an ACL file, and that ACL file is empty, or contains only comments or blank lines, then Mosquitto will treat this as though no ACL file has been defined and use a default allow policy. The new behaviour is to have an empty ACL file mean that all access is denied, which is not a useful configuration but is not unexpected.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00035.html
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=541870
