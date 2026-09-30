# [H] CVE-2021-31822

## Summary
Severity: High
Advisory: CVE-2021-31822
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/CVE-2021-31822
Type: osv

## Details
When Octopus Tentacle is installed on a Linux operating system, the systemd service file permissions are misconfigured. This could lead to a local unprivileged user modifying the contents of the systemd service file to gain privileged access.

## References
- https://advisories.octopus.com/adv/2021-11---Local-privilege-escalation-in-Octopus-Tentacle-%28CVE-2021-31822%29.2283732993.html
