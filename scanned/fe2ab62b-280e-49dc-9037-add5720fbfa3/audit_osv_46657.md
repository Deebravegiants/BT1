# [H] CVE-2014-7272

## Summary
Severity: High
Advisory: CVE-2014-7272
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-08
Source: https://osv.dev/vulnerability/CVE-2014-7272
Type: osv

## Details
Simple Desktop Display Manager (SDDM) before 0.10.0 allows local users to gain root privileges because code running as root performs write operations within a user home directory, and this user may have created links in advance (exploitation requires the user to win a race condition in the ~/.Xauthority chown case, but not other cases).

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/141494.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-October/141550.html
- http://www.openwall.com/lists/oss-security/2014/10/06/4
- http://www.openwall.com/lists/oss-security/2014/10/06/4
- https://github.com/sddm/sddm/pull/280
- https://bugzilla.redhat.com/show_bug.cgi?id=1149610
