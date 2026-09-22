# [H] CVE-2018-19358

## Summary
Severity: High
Advisory: CVE-2018-19358
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-18
Source: https://osv.dev/vulnerability/CVE-2018-19358
Type: osv

## Details
GNOME Keyring through 3.28.2 allows local users to retrieve login credentials via a Secret Service API call and the D-Bus interface if the keyring is unlocked, a similar issue to CVE-2008-7320. One perspective is that this occurs because available D-Bus protection mechanisms (involving the busconfig and policy XML elements) are not used. NOTE: the vendor disputes this because, according to the security model, untrusted applications must not be allowed to access the user's session bus socket.

## References
- https://bugs.launchpad.net/ubuntu/+source/gnome-keyring/+bug/1780365
- https://bugzilla.redhat.com/show_bug.cgi?id=1652194#c8
- https://gitlab.gnome.org/GNOME/gnome-keyring/-/issues/5#note_1876550
- https://github.com/sungjungk/keyring_crack
- https://www.youtube.com/watch?v=Do4E9ZQaPck
