# [H] CVE-2024-5290

## Summary
Severity: High
Advisory: CVE-2024-5290
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-5290
Type: osv

## Details
An issue was discovered in Ubuntu wpa_supplicant that resulted in loading of arbitrary shared objects, which allows a local unprivileged attacker to escalate privileges to the user that wpa_supplicant runs as (usually root).




Membership in the netdev group or access to the dbus interface of wpa_supplicant allow an unprivileged user to specify an arbitrary path to a module to be loaded by the wpa_supplicant process; other escalation paths might exist.

## References
- https://snyk.io/blog/abusing-ubuntu-root-privilege-escalation/
- https://ubuntu.com/security/notices/USN-6945-1
- https://bugs.launchpad.net/ubuntu/+source/wpa/+bug/2067613
- https://snyk.io/blog/abusing-ubuntu-root-privilege-escalation/
- https://bugs.launchpad.net/ubuntu/+source/wpa/+bug/2067613
