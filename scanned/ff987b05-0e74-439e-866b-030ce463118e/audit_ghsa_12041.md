# [M] Moby has an Off-by-one error in its plugin privilege validation

## Summary
Severity: Medium
Advisory: GHSA-pxq6-2prw-chj9
CVE: CVE-2026-33997
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-pxq6-2prw-chj9
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0
- Go: `github.com/moby/moby/v2` — affected >=0 <2.0.0-beta.8
- Go: `github.com/moby/moby` — affected >=0

## Details
## Summary

A security vulnerability has been detected that allows [plugins](https://docs.docker.com/engine/extend/legacy_plugins/) privilege validation to be bypassed during `docker plugin install`. Due to an error in the daemon's privilege comparison logic, the daemon may incorrectly accept a privilege set that differs from the one approved by the user.

Plugins that request exactly one privilege are also affected, because no comparison is performed at all.

## Impact

**If plugins are not in use, there is no impact.**

When a plugin is installed, the daemon computes the privileges required by the plugin's configuration and compares them with the privileges approved during installation. A malicious plugin can exploit this bug so that the daemon accepts privileges that differ from what was intended to be approved.

Anyone who depends on the plugin installation approval flow as a meaningful security boundary is potentially impacted.

Depending on the privilege set involved, this may include highly sensitive plugin permissions such as broad device access.

**For consideration: exploitation still requires a plugin to be installed from a malicious source, and Docker plugins are relatively uncommon. Docker Desktop also does not support plugins.**

## Workarounds

If unable to update immediately:
- Do not install plugins from untrusted sources
- Carefully review all privileges requested during `docker plugin install`
- Restrict access to the Docker daemon to trusted parties, following the principle of least privilege
- Avoid relying on plugin privilege approval as the only control boundary for sensitive environments

## Credits

- Reported by Cody (c@wormhole.guru, PGP 0x9FA5B73E)

## References
- https://github.com/moby/moby/security/advisories/GHSA-pxq6-2prw-chj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33997
- https://github.com/moby/moby/commit/f4d6f25bf0c3fa12d4968320a45685947756a22a
- https://docs.docker.com/engine/extend/legacy_plugins
- https://github.com/moby/moby
- https://github.com/moby/moby/releases/tag/docker-v29.3.1
