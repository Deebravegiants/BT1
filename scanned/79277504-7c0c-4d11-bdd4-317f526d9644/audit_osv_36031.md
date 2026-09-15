# [M] Policycoreutils: policycoreutils: toctou race condition in fixfiles allows arbitrary selinux label manipulation

## Summary
Severity: Medium
Advisory: CVE-2026-19079
CVSS: 4.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-19079
Type: osv

## Details
A TOCTOU (Time-of-Check-Time-of-Use) race condition vulnerability was found in the fixfiles script in policycoreutils. When running fixfiles relabel or fixfiles restore, the script used find and chcon commands to locate and relabel unlabeled files under /tmp and other directories. A local attacker could exploit a race window between the file discovery and the label change operation by swapping directory components with symlinks, causing chcon to follow the symlink and modify SELinux labels on arbitrary system files. This could undermine SELinux mandatory access control protections on critical files such as /etc/shadow.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:51861
- https://access.redhat.com/security/cve/CVE-2026-19079
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19079.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19079
- https://bugzilla.redhat.com/show_bug.cgi?id=2511976
- https://github.com/SELinuxProject/selinux/commit/a556538c2d5d2583273e025b45c02651fef47679
