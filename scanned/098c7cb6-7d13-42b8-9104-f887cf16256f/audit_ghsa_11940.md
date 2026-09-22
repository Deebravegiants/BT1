# [C] Incus has an abitrary file write through its systemd-creds options

## Summary
Severity: Critical
Advisory: GHSA-q4q8-7f2j-9h9f
CVE: CVE-2026-33945
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-q4q8-7f2j-9h9f
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6` — affected >=0 <6.23.0

## Details
### Summary
Incus instances have an option to provide credentials to systemd in the guest. For containers, this is handled through a shared directory.
An attacker can use the name of a systemd credential to escape that directory and overwrite arbitrary files on the host system.

This can in turn be used to perform local privilege escalation or cause a DoS.

### Details
An attacker can set a configuration key named something like `systemd.credential.../../../../../../root/.bashrc` to cause Incus to write outside of the `credentials` directory associated with the container. This makes use of the fact that the Incus syntax for such credentials is `systemd.credential.XYZ` where `XYZ` can itself contain more periods.

While it's not possible to read any data this way, it's possible to write to arbitrary files as root, enabling both privilege escalation and denial of service attacks.

### Credit
This issue was discovered and reported by the team at [7asecurity](https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-q4q8-7f2j-9h9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33945
- https://github.com/lxc/incus/commit/f74199f9983e2ce78f2b78b6d765c6635b229c82
- https://github.com/lxc/incus
