# [M] CVE-2018-1063

## Summary
Severity: Medium
Advisory: CVE-2018-1063
CVSS: 4.4 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2018-1063
Type: osv

## Details
Context relabeling of filesystems is vulnerable to symbolic link attack, allowing a local, unprivileged malicious entity to change the SELinux context of an arbitrary file to a context with few restrictions. This only happens when the relabeling process is done, usually when taking SELinux state from disabled to enable (permissive or enforcing). The issue was found in policycoreutils 2.5-11.

## References
- https://access.redhat.com/errata/RHSA-2018:0913
- https://bugzilla.redhat.com/show_bug.cgi?id=1550122
