# [H] CVE-2020-1716

## Summary
Severity: High
Advisory: CVE-2020-1716
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2020-1716
Type: osv

## Details
A flaw was found in the ceph-ansible playbook where it contained hardcoded passwords that were being used as default passwords while deploying Ceph services. Any authenticated attacker can abuse this flaw to brute-force Ceph deployments, and gain administrator access to Ceph clusters via the Ceph dashboard to initiate read, write, and delete Ceph clusters and also modify Ceph cluster configurations. Versions before ceph-ansible 6.0.0alpha1 are affected.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1795592
