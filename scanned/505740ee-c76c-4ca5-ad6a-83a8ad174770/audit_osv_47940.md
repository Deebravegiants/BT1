# [H] CVE-2017-15139

## Summary
Severity: High
Advisory: CVE-2017-15139
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-27
Source: https://osv.dev/vulnerability/CVE-2017-15139
Type: osv

## Details
A vulnerability was found in openstack-cinder releases up to and including Queens, allowing newly created volumes in certain storage volume configurations to contain previous data. It specifically affects ScaleIO volumes using thin volumes and zero padding. This could lead to leakage of sensitive information between tenants.

## References
- https://access.redhat.com/errata/RHSA-2018:3601
- https://access.redhat.com/errata/RHSA-2019:0917
- https://wiki.openstack.org/wiki/OSSN/OSSN-0084
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-15139
