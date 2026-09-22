# [M] CVE-2025-6966

## Summary
Severity: Medium
Advisory: CVE-2025-6966
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-6966
Type: osv

## Details
NULL pointer dereference in TagSection.keys() in python-apt on APT-based Linux systems allows a local attacker to cause a denial of service (process crash) via a crafted deb822 file with a malformed non-UTF-8 key.

## References
- https://lists.debian.org/debian-lts-announce/2025/12/msg00019.html
- https://bugs.launchpad.net/ubuntu/+source/python-apt/+bug/2091865
