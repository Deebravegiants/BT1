# [H] CVE-2021-26720

## Summary
Severity: High
Advisory: CVE-2021-26720
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2021-26720
Type: osv

## Details
avahi-daemon-check-dns.sh in the Debian avahi package through 0.8-4 is executed as root via /etc/network/if-up.d/avahi-daemon, and allows a local attacker to cause a denial of service or create arbitrary empty files via a symlink attack on files under /run/avahi-daemon. NOTE: this only affects the packaging for Debian GNU/Linux (used indirectly by SUSE), not the upstream Avahi product.

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=982796
- https://lists.debian.org/debian-lts-announce/2022/06/msg00009.html
- https://metadata.ftp-master.debian.org/changelogs/main/a/avahi/avahi_0.8-4_changelog
- https://packages.debian.org/bullseye/avahi-daemon
- https://packages.debian.org/buster/avahi-daemon
- https://packages.debian.org/sid/avahi-daemon
- https://security-tracker.debian.org/tracker/CVE-2021-26720
- https://www.openwall.com/lists/oss-security/2021/02/15/2
- https://bugs.launchpad.net/ubuntu/+source/avahi/+bug/1870824
- https://bugzilla.suse.com/show_bug.cgi?id=1180827
