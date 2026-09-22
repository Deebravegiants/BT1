# [H] CVE-2018-20781

## Summary
Severity: High
Advisory: CVE-2018-20781
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-12
Source: https://osv.dev/vulnerability/CVE-2018-20781
Type: osv

## Details
In pam/gkr-pam-module.c in GNOME Keyring before 3.27.2, the user's password is kept in a session-child process spawned from the LightDM daemon. This can expose the credential in cleartext.

## References
- https://github.com/huntergregal/mimipenguin
- https://github.com/huntergregal/mimipenguin/tree/d95f1e08ce79783794f38433bbf7de5abd9792da
- https://gitlab.gnome.org/GNOME/gnome-keyring/issues/3
- https://gitlab.gnome.org/GNOME/gnome-keyring/tags/3.27.2
- https://usn.ubuntu.com/3894-1/
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://bugs.launchpad.net/ubuntu/+source/gnome-keyring/+bug/1772919
- https://bugzilla.gnome.org/show_bug.cgi?id=781486
