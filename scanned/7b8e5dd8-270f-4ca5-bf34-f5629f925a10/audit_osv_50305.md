# [M] CVE-2020-11934

## Summary
Severity: Medium
Advisory: CVE-2020-11934
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-11934
Type: osv

## Details
It was discovered that snapctl user-open allowed altering the $XDG_DATA_DIRS environment variable when calling the system xdg-open. OpenURL() in usersession/userd/launcher.go would alter $XDG_DATA_DIRS to append a path to a directory controlled by the calling snap. A malicious snap could exploit this to bypass intended access restrictions to control how the host system xdg-open script opens the URL and, for example, execute a script shipped with the snap without confinement. This issue did not affect Ubuntu Core systems. Fixed in snapd versions 2.45.1ubuntu0.2, 2.45.1+18.04.2 and 2.45.1+20.04.2.

## References
- https://launchpad.net/bugs/1880085
- https://ubuntu.com/USN-4424-1
