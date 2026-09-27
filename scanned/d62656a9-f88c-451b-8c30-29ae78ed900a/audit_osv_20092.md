# [H] CVE-2021-3020

## Summary
Severity: High
Advisory: CVE-2021-3020
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-3020
Type: osv

## Details
An issue was discovered in ClusterLabs Hawk (aka HA Web Konsole) through 2.3.0-15. It ships the binary hawk_invoke (built from tools/hawk_invoke.c), intended to be used as a setuid program. This allows the hacluster user to invoke certain commands as root (with an attempt to limit this to safe combinations). This user is able to execute an interactive "shell" that isn't limited to the commands specified in hawk_invoke, allowing escalation to root.

## References
- https://github.com/ClusterLabs/hawk/releases
- https://bugzilla.suse.com/show_bug.cgi?id=1180571
- https://github.com/ClusterLabs/crmsh/commit/c538024b8ebd138dc373b005189471d9b77e9c82
