# [M] Non-interactive Tailscale SSH sessions on FreeBSD may use the effective group ID of the tailscaled process

## Summary
Severity: Medium
Advisory: GHSA-vfgq-g5x8-g595
CVE: CVE-2023-28436
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.0/AV:A/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-vfgq-g5x8-g595
Type: github-advisory

## Affected
- Go: `tailscale.com` — affected >=1.34.0 <1.38.2

## Details
A vulnerability identified in the implementation of Tailscale SSH in FreeBSD allowed commands to be run with a higher privilege group ID than that specified by Tailscale SSH access rules.

**Affected platforms**: FreeBSD

**Patched Tailscale client versions**: v1.38.2 or later

### What happened?
A difference in the behavior of the FreeBSD `setgroups` system call from POSIX meant that the Tailscale client running on a FreeBSD-based operating system did not appropriately restrict groups on the host when using Tailscale SSH. When accessing a FreeBSD host over Tailscale SSH, the egid of the tailscaled process was used instead of that of the user specified in Tailscale SSH access rules.

### Who is affected?
9 tailnets with 22 FreeBSD nodes running Tailscale SSH since Tailscale v1.34 (released on 2022-12-04) may have had Tailscale SSH sessions with a higher privilege group ID than that specified in Tailscale SSH access rules.

We have notified the affected organizations where we have [security contacts](https://tailscale.com/kb/1224/contact-preferences/#setting-the-security-issues-email).

### What is the impact?
Tailscale SSH commands may have been run with a higher privilege group ID than that specified in Tailscale SSH access rules if they met all of the following criteria:
* The destination node was a FreeBSD device with Tailscale SSH enabled;
* Tailscale SSH access rules permitted access for non-root users; and
* A non-interactive SSH session was used.

### What do I need to do?
If you are running Tailscale on FreeBSD, upgrade to v1.38.2 or later to remediate the issue. Admins of a tailnet can view [FreeBSD nodes with unpatched versions](https://login.tailscale.com/admin/machines?q=version%3A%3C1.38.2+freebsd) in the admin console.

To update the local ports tree in advance of what's available upstream, you can:

1. `cd /usr/ports/security/tailscale`
2. edit the Makefile to set `PORTVERSION` to `1.38.2`
3. `make makesum`
4. `make install`

Tailscale SSH on other platforms is not affected.

### Credits
We would like to thank [Ryan Belgrave](https://www.linkedin.com/in/rbelgrave/) for reporting this issue.

### References
* [TS-2023-003](https://tailscale.com/security-bulletins/#ts-2023-003)

## References
- https://github.com/tailscale/tailscale/security/advisories/GHSA-vfgq-g5x8-g595
- https://nvd.nist.gov/vuln/detail/CVE-2023-28436
- https://github.com/tailscale/tailscale/commit/d00c046b723dff6e3775d7d35f891403ac21a47d
- https://github.com/tailscale/tailscale
- https://github.com/tailscale/tailscale/releases/tag/v1.38.2
- https://tailscale.com/security-bulletins/#ts-2023-003
