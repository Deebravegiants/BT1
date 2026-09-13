# [H] CVE-2020-14352

## Summary
Severity: High
Advisory: CVE-2020-14352
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-08-30
Source: https://osv.dev/vulnerability/CVE-2020-14352
Type: osv

## Details
A flaw was found in librepo in versions before 1.12.1. A directory traversal vulnerability was found where it failed to sanitize paths in remote repository metadata. An attacker controlling a remote repository may be able to copy files outside of the destination directory on the targeted system via path traversal. This flaw could potentially result in system compromise via the overwriting of critical system files. The highest threat from this flaw is to users that make use of untrusted third-party repositories.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/33RX4P5R5YL4NZSFSE4NOX37X6YCXAS4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OOMDEQBRJ7SO2QWL7H23G3VV2VSCUYOY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XDMHVY7OMIJNSPVZ2GJWHT77Z5V3YJ55/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00072.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1866498
