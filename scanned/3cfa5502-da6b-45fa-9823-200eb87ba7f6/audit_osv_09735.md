# [M] CVE-2017-11171

## Summary
Severity: Medium
Advisory: CVE-2017-11171
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-11
Source: https://osv.dev/vulnerability/CVE-2017-11171
Type: osv

## Details
Bad reference counting in the context of accept_ice_connection() in gsm-xsmp-server.c in old versions of gnome-session up until version 2.29.92 allows a local attacker to establish ICE connections to gnome-session with invalid authentication data (an invalid magic cookie). Each failed authentication attempt will leak a file descriptor in gnome-session. When the maximum number of file descriptors is exhausted in the gnome-session process, it will enter an infinite loop trying to communicate without success, consuming 100% of the CPU. The graphical session associated with the gnome-session process will stop working correctly, because communication with gnome-session is no longer possible.

## References
- https://github.com/GNOME/gnome-session/commit/b0dc999e0b45355314616321dbb6cb71e729fc9d
- https://bugzilla.suse.com/show_bug.cgi?id=1025068
