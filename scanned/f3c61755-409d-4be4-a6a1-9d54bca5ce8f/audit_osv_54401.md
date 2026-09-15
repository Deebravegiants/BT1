# [M] CVE-2023-5616

## Summary
Severity: Medium
Advisory: CVE-2023-5616
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2023-5616
Type: osv

## Details
In Ubuntu, gnome-control-center did not properly reflect SSH remote login status when the system was configured to use systemd socket activation for openssh-server. This could unknowingly leave the local machine exposed to remote SSH access contrary to expectation of the user.

## References
- https://ubuntu.com/security/CVE-2023-5616
- https://ubuntu.com/security/notices/USN-6554-1
- https://bugs.launchpad.net/ubuntu/+source/gnome-control-center/+bug/2039577
