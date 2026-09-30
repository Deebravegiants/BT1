# [M] CVE-2020-25677

## Summary
Severity: Medium
Advisory: CVE-2020-25677
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-25677
Type: osv

## Details
A flaw was found in Ceph-ansible v4.0.41 where it creates an /etc/ceph/iscsi-gateway.conf with insecure default permissions. This flaw allows any user on the system to read sensitive information within this file. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1892108
