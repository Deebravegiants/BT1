# [H] Tmds.DBus: malicious D-Bus peers can spoof signals, exhaust file descriptor resources, and cause denial of service

## Summary
Severity: High
Advisory: GHSA-xrw6-gwf8-vvr9
CVE: CVE-2026-39959
CWE: CWE-290, CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-xrw6-gwf8-vvr9
Type: github-advisory

## Affected
- NuGet: `Tmds.DBus` — affected >=0 <0.92.0
- NuGet: `Tmds.DBus.Protocol` — affected >=0 <0.21.3
- NuGet: `Tmds.DBus.Protocol` — affected >=0.22.0 <0.92.0

## Details
Tmds.DBus and Tmds.DBus.Protocol are vulnerable to malicious D-Bus peers. A peer on the same bus can spoof signals by impersonating the owner of a well-known name, exhaust system resources or cause file descriptor spillover by sending messages with an excessive number of Unix file descriptors, and crash the application by sending malformed message bodies that cause unhandled exceptions on the SynchronizationContext.

### Patches

The vulnerabilities are fixed in version 0.92.0.
For Tmds.DBus.Protocol, the fixes are also backported to 0.21.3.

### Workarounds

There are no known workarounds. Users should upgrade to a patched version.

## References
- https://github.com/tmds/Tmds.DBus/security/advisories/GHSA-xrw6-gwf8-vvr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39959
- https://github.com/tmds/Tmds.DBus
- https://github.com/tmds/Tmds.DBus/releases/tag/rel%2F0.21.3
- https://github.com/tmds/Tmds.DBus/releases/tag/rel%2F0.92.0
