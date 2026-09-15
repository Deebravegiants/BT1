# [H] CVE-2019-14822

## Summary
Severity: High
Advisory: CVE-2019-14822
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-14822
Type: osv

## Details
A flaw was discovered in ibus in versions before 1.5.22 that allows any unprivileged user to monitor and send method calls to the ibus bus of another user due to a misconfiguration in the DBus server setup. A local attacker may use this flaw to intercept all keystrokes of a victim user who is using the graphical interface, change the input method engine, or modify other input related configurations of the victim user.

## References
- https://usn.ubuntu.com/4134-3/
- https://bugzilla.redhat.com/show_bug.cgi?id=1717958
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14822
- https://www.oracle.com/security-alerts/cpuapr2022.html
