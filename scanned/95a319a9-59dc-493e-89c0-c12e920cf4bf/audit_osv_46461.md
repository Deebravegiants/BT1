# [M] CVE-2011-2923

## Summary
Severity: Medium
Advisory: CVE-2011-2923
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-19
Source: https://osv.dev/vulnerability/CVE-2011-2923
Type: osv

## Details
foomatic-rip filter, all versions, used insecurely creates temporary files for storage of PostScript data by rendering the data when the debug mode was enabled. This flaw may be exploited by a local attacker to conduct symlink attacks by overwriting arbitrary files accessible with the privileges of the user running the foomatic-rip universal print filter.

## References
- https://access.redhat.com/security/cve/cve-2011-2923
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-2923
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2011-2923
- https://security-tracker.debian.org/tracker/CVE-2011-2923
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-2923
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2011-2923
