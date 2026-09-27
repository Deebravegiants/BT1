# [C] CVE-2017-9269

## Summary
Severity: Critical
Advisory: CVE-2017-9269
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-9269
Type: osv

## Details
In libzypp before August 2018 GPG keys attached to YUM repositories were not correctly pinned, allowing malicious repository mirrors to silently downgrade to unsigned repositories with potential malicious content.

## References
- https://www.suse.com/de-de/security/cve/CVE-2017-9269/
- https://lists.opensuse.org/opensuse-security-announce/2017-08/msg00002.html
- https://bugzilla.suse.com/show_bug.cgi?id=1045735
