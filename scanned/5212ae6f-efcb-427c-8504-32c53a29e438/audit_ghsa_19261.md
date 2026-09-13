# [H] Yggdrasil Vulnerable to Local Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-rpg2-jvhp-h354
CVE: CVE-2025-3931
CWE: CWE-280
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-rpg2-jvhp-h354
Type: github-advisory

## Affected
- Go: `github.com/redhatinsights/yggdrasil` — affected >=0

## Details
A flaw was found in Yggdrasil, which acts as a system broker, allowing the processes to communicate to other children's "worker" processes through the DBus component. Yggdrasil creates a DBus method to dispatch messages to workers. However, it misses authentication and authorization checks, allowing every system user to call it. One available Yggdrasil worker acts as a package manager with capabilities to create and enable new repositories and install or remove packages. 

This flaw allows an attacker with access to the system to leverage the lack of authentication on the dispatch message to force the Yggdrasil worker to install arbitrary RPM packages. This issue results in local privilege escalation, enabling the attacker to access and modify sensitive system data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3931
- https://github.com/RedHatInsights/yggdrasil/pull/336
- https://github.com/RedHatInsights/yggdrasil/commit/196d0cbea42f72e6dfecaa563681a99e9fdb4a38
- https://access.redhat.com/errata/RHSA-2025:7592
- https://access.redhat.com/security/cve/CVE-2025-3931
- https://bugzilla.redhat.com/show_bug.cgi?id=2362345
- https://github.com/RedHatInsights/yggdrasil
