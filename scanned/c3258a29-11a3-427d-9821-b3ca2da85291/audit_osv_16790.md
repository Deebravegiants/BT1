# [H] CVE-2019-9755

## Summary
Severity: High
Advisory: CVE-2019-9755
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-9755
Type: osv

## Details
An integer underflow issue exists in ntfs-3g 2017.3.23. A local attacker could potentially exploit this by running /bin/ntfs-3g with specially crafted arguments from a specially crafted directory to cause a heap buffer overflow, resulting in a crash or the ability to execute arbitrary code. In installations where /bin/ntfs-3g is a setuid-root binary, this could lead to a local escalation of privileges.

## References
- https://access.redhat.com/errata/RHBA-2019:3723
- https://access.redhat.com/errata/RHSA-2019:2308
- https://access.redhat.com/errata/RHSA-2019:3345
- https://security.gentoo.org/glsa/202007-45
- https://www.tuxera.com/community/release-history/
