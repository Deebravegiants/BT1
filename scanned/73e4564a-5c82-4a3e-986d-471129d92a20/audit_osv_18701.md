# [H] CVE-2020-35512

## Summary
Severity: High
Advisory: CVE-2020-35512
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/CVE-2020-35512
Type: osv

## Details
A use-after-free flaw was found in D-Bus Development branch <= 1.13.16, dbus-1.12.x stable branch <= 1.12.18, and dbus-1.10.x and older branches <= 1.10.30 when a system has multiple usernames sharing the same UID. When a set of policy rules references these usernames, D-Bus may free some memory in the heap, which is still used by data structures necessary for the other usernames sharing the UID, possibly leading to a crash or other undefined behaviors

## References
- https://security-tracker.debian.org/tracker/CVE-2020-35512
- https://bugs.gentoo.org/755392
- https://bugzilla.redhat.com/show_bug.cgi?id=1909101
- https://gitlab.freedesktop.org/dbus/dbus/-/issues/305#note_829128
