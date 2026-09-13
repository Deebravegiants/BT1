# [H] CVE-2011-3349

## Summary
Severity: High
Advisory: CVE-2011-3349
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-19
Source: https://osv.dev/vulnerability/CVE-2011-3349
Type: osv

## Details
lightdm before 0.9.6 writes in .dmrc and Xauthority files using root permissions while the files are in user controlled folders. A local user can overwrite root-owned files via a symlink, which can allow possible privilege escalation.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=639151
- https://bugs.launchpad.net/debian/+source/lightdm/+bug/834079
- https://seclists.org/oss-sec/2011/q3/393
- https://security-tracker.debian.org/tracker/CVE-2011-3349
- https://www.securityfocus.com/bid/50506
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=639151
- https://seclists.org/oss-sec/2011/q3/393
- https://access.redhat.com/security/cve/cve-2011-3349
