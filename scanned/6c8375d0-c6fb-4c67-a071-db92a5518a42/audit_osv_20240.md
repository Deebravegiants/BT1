# [M] CVE-2021-32553

## Summary
Severity: Medium
Advisory: CVE-2021-32553
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-12
Source: https://osv.dev/vulnerability/CVE-2021-32553
Type: osv

## Details
It was discovered that read_file() in apport/hookutils.py would follow symbolic links or open FIFOs. When this function is used by the openjdk-17 package apport hooks, it could expose private data to other local users.

## References
- https://bugs.launchpad.net/ubuntu/+source/apport/+bug/1917904
