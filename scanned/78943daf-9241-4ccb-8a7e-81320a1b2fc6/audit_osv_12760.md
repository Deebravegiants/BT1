# [C] CVE-2018-14649

## Summary
Severity: Critical
Advisory: CVE-2018-14649
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-09
Source: https://osv.dev/vulnerability/CVE-2018-14649
Type: osv

## Details
It was found that ceph-isci-cli package as shipped by Red Hat Ceph Storage 2 and 3 is using python-werkzeug in debug shell mode. This is done by setting debug=True in file /usr/bin/rbd-target-api provided by ceph-isci-cli package. This allows unauthenticated attackers to access this debug shell and escalate privileges. Once an attacker has successfully connected to this debug shell they will be able to execute arbitrary commands remotely. These commands will run with the same privileges as of user executing the application which is using python-werkzeug with debug shell mode enabled. In - Red Hat Ceph Storage 2 and 3, ceph-isci-cli package runs python-werkzeug library with root level permissions.

## References
- http://www.securityfocus.com/bid/105434
- https://access.redhat.com/errata/RHSA-2018:2837
- https://access.redhat.com/errata/RHSA-2018:2838
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14649
- https://access.redhat.com/articles/3623521
- https://github.com/ceph/ceph-iscsi-cli/pull/121/commits/c3812075e30c76a800a961e7291087d357403f6b
- https://github.com/ceph/ceph-iscsi-cli/issues/120
