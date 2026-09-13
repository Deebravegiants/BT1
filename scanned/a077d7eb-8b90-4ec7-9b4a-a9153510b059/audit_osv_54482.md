# [M] CVE-2023-6917

## Summary
Severity: Medium
Advisory: CVE-2023-6917
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2023-6917
Type: osv

## Details
A vulnerability has been identified in the Performance Co-Pilot (PCP) package, stemming from the mixed privilege levels utilized by systemd services associated with PCP. While certain services operate within the confines of limited PCP user/group privileges, others are granted full root privileges. This disparity in privilege levels poses a risk when privileged root processes interact with directories or directory trees owned by unprivileged PCP users. Specifically, this vulnerability may lead to the compromise of PCP user isolation and facilitate local PCP-to-root exploits, particularly through symlink attacks. These vulnerabilities underscore the importance of maintaining robust privilege separation mechanisms within PCP to mitigate the potential for unauthorized privilege escalation.

## References
- https://access.redhat.com/errata/RHSA-2024:2213
- https://access.redhat.com/security/cve/CVE-2023-6917
- https://bugzilla.redhat.com/show_bug.cgi?id=2254983
