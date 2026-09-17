# [M] CVE-2018-10916

## Summary
Severity: Medium
Advisory: CVE-2018-10916
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2018-10916
Type: osv

## Details
It has been discovered that lftp up to and including version 4.8.3 does not properly sanitize remote file names, leading to a loss of integrity on the local system when reverse mirroring is used. A remote attacker may trick a user to use reverse mirroring on an attacker controlled FTP server, resulting in the removal of all files in the current working directory of the victim's system.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00036.html
- https://usn.ubuntu.com/3731-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10916
- https://github.com/lavv17/lftp/commit/a27e07d90a4608ceaf928b1babb27d4d803e1992
- https://github.com/lavv17/lftp/issues/452
