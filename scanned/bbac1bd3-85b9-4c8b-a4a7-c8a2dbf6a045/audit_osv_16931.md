# [M] CVE-2020-10744

## Summary
Severity: Medium
Advisory: CVE-2020-10744
Aliases: GHSA-vp9j-rghq-8jhh, PYSEC-2020-208
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:L)
Published: 2020-05-15
Source: https://osv.dev/vulnerability/CVE-2020-10744
Type: osv

## Details
An incomplete fix was found for the fix of the flaw CVE-2020-1733 ansible: insecure temporary directory when running become_user from become directive. The provided fix is insufficient to prevent the race condition on systems using ACLs and FUSE filesystems. Ansible Engine 2.7.18, 2.8.12, and 2.9.9 as well as previous versions are affected and Ansible Tower 3.4.5, 3.5.6 and 3.6.4 as well as previous versions are affected.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10744
