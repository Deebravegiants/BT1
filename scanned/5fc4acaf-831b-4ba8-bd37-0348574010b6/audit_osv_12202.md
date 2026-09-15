# [H] CVE-2018-10896

## Summary
Severity: High
Advisory: CVE-2018-10896
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2018-10896
Type: osv

## Details
The default cloud-init configuration, in cloud-init 0.6.2 and newer, included "ssh_deletekeys: 0", disabling cloud-init's deletion of ssh host keys. In some environments, this could lead to instances created by cloning a golden master or template system, sharing ssh host keys, and being able to impersonate one another or conduct man-in-the-middle attacks.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1574338
- https://bugs.launchpad.net/cloud-init/+bug/1781094
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10896
