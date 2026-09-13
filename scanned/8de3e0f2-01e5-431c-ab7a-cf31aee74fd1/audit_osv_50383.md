# [M] CVE-2020-14367

## Summary
Severity: Medium
Advisory: CVE-2020-14367
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/CVE-2020-14367
Type: osv

## Details
A flaw was found in chrony versions before 3.5.1 when creating the PID file under the /var/run/chrony folder. The file is created during chronyd startup while still running as the root user, and when it's opened for writing, chronyd does not check for an existing symbolic link with the same file name. This flaw allows an attacker with privileged access to create a symlink with the default PID file name pointing to any destination file in the system, resulting in data loss and a denial of service due to the path traversal.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6WKABKNLCSC3MACCWU6OM2YGWVWFWFMU/
- https://security.gentoo.org/glsa/202008-23
- https://usn.ubuntu.com/4475-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1870298
