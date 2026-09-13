# [M] CVE-2026-4105

## Summary
Severity: Medium
Advisory: CVE-2026-4105
Aliases: GHSA-4h6x-r8vx-3862
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-4105
Type: osv

## Details
A flaw was found in systemd. The systemd-machined service contains an Improper Access Control vulnerability due to insufficient validation of the class parameter in the RegisterMachine D-Bus (Desktop Bus) method. A local unprivileged user can exploit this by attempting to register a machine with a specific class value, which may leave behind a usable, attacker-controlled machine object. This allows the attacker to invoke methods on the privileged object, leading to the execution of arbitrary commands with root privileges on the host system.

## References
- https://access.redhat.com/security/cve/CVE-2026-4105
- https://github.com/systemd/systemd/security/advisories/GHSA-4h6x-r8vx-3862
- https://bugzilla.redhat.com/show_bug.cgi?id=2447262
