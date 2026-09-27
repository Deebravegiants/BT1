# [M] CVE-2024-5742

## Summary
Severity: Medium
Advisory: CVE-2024-5742
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-12
Source: https://osv.dev/vulnerability/CVE-2024-5742
Type: osv

## Details
A vulnerability was found in GNU Nano that allows a possible privilege escalation through an insecure temporary file. If Nano is killed while editing, a file it saves to an emergency file with the permissions of the running user provides a window of opportunity for attackers to escalate privileges through a malicious symlink.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00006.html
- https://access.redhat.com/errata/RHSA-2024:6986
- https://access.redhat.com/errata/RHSA-2024:9430
- https://access.redhat.com/security/cve/CVE-2024-5742
- https://bugzilla.redhat.com/show_bug.cgi?id=2278574
