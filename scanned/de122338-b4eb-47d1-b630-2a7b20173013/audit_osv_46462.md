# [M] CVE-2011-2924

## Summary
Severity: Medium
Advisory: CVE-2011-2924
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-11-19
Source: https://osv.dev/vulnerability/CVE-2011-2924
Type: osv

## Details
foomatic-rip filter v4.0.12 and prior used insecurely creates temporary files for storage of PostScript data by rendering the data when the debug mode was enabled. This flaw may be exploited by a local attacker to conduct symlink attacks by overwriting arbitrary files accessible with the privileges of the user running the foomatic-rip universal print filter.

## References
- https://access.redhat.com/security/cve/cve-2011-2924
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-2924
- https://launchpad.net/ubuntu/+source/foomatic-filters/4.0.12-1
- https://lwn.net/Articles/459979/
- https://security-tracker.debian.org/tracker/CVE-2011-2924
- https://www.openwall.com/lists/oss-security/2014/02/08/5/1
- https://www.openwall.com/lists/oss-security/2014/02/08/5/1
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-2924
