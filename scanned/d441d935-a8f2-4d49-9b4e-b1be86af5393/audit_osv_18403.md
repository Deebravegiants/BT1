# [H] CVE-2020-27352

## Summary
Severity: High
Advisory: CVE-2020-27352
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2020-27352
Type: osv

## Details
When generating the systemd service units for the docker snap (and other similar snaps), snapd does not specify Delegate=yes - as a result systemd will move processes from the containers created and managed by these snaps into the cgroup of the main daemon within the snap itself when reloading system units. This may grant additional privileges to a container within the snap that were not originally intended.

## References
- https://ubuntu.com/security/notices/USN-4728-1
- https://www.cve.org/CVERecord?id=CVE-2020-27352
- https://bugs.launchpad.net/snapd/+bug/1910456
