# [M] CVE-2020-16125

## Summary
Severity: Medium
Advisory: CVE-2020-16125
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-10
Source: https://osv.dev/vulnerability/CVE-2020-16125
Type: osv

## Details
gdm3 versions before 3.36.2 or 3.38.2 would start gnome-initial-setup if gdm3 can't contact the accountservice service via dbus in a timely manner; on Ubuntu (and potentially derivatives) this could be be chained with an additional issue that could allow a local user to create a new privileged account.

## References
- https://bugs.launchpad.net/ubuntu/+source/gdm3/+bug/1900314
- https://gitlab.gnome.org/GNOME/gdm/-/issues/642
- https://securitylab.github.com/advisories/GHSL-2020-202-gdm3-LPE-unresponsive-accounts-daemon
