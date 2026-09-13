# [M] CVE-2020-8631

## Summary
Severity: Medium
Advisory: CVE-2020-8631
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-02-05
Source: https://osv.dev/vulnerability/CVE-2020-8631
Type: osv

## Details
cloud-init through 19.4 relies on Mersenne Twister for a random password, which makes it easier for attackers to predict passwords, because rand_str in cloudinit/util.py calls the random.choice function.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00042.html
- https://lists.debian.org/debian-lts-announce/2020/02/msg00021.html
- https://bugs.launchpad.net/ubuntu/+source/cloud-init/+bug/1860795
- https://github.com/canonical/cloud-init/pull/204
