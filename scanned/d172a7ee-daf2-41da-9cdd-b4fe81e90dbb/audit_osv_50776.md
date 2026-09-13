# [M] CVE-2020-5202

## Summary
Severity: Medium
Advisory: CVE-2020-5202
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-01-21
Source: https://osv.dev/vulnerability/CVE-2020-5202
Type: osv

## Details
apt-cacher-ng through 3.3 allows local users to obtain sensitive information by hijacking the hardcoded TCP port. The /usr/lib/apt-cacher-ng/acngtool program attempts to connect to apt-cacher-ng via TCP on localhost port 3142, even if the explicit SocketPath=/var/run/apt-cacher-ng/socket command-line option is passed. The cron job /etc/cron.daily/apt-cacher-ng (which is active by default) attempts this periodically. Because 3142 is an unprivileged port, any local user can try to bind to this port and will receive requests from acngtool. There can be sensitive data in these requests, e.g., if AdminAuth is enabled in /etc/apt-cacher-ng/security.conf. This sensitive data can leak to unprivileged local users that manage to bind to this port before the apt-cacher-ng daemon can.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00057.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00065.html
- https://security-tracker.debian.org/tracker/CVE-2020-5202
- http://www.openwall.com/lists/oss-security/2020/01/20/4
- https://seclists.org/oss-sec/2020/q1/21
