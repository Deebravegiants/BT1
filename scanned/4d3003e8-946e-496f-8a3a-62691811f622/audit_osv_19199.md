# [M] CVE-2020-8632

## Summary
Severity: Medium
Advisory: CVE-2020-8632
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-05
Source: https://osv.dev/vulnerability/CVE-2020-8632
Type: osv

## Details
In cloud-init through 19.4, rand_user_password in cloudinit/config/cc_set_passwords.py has a small default pwlen value, which makes it easier for attackers to guess passwords.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00042.html
- https://lists.debian.org/debian-lts-announce/2020/02/msg00021.html
- https://bugs.launchpad.net/ubuntu/+source/cloud-init/+bug/1860795
- https://github.com/canonical/cloud-init/pull/189
