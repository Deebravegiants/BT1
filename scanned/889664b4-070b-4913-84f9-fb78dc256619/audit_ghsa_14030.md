# [H] sccache vulnerable to privilege escalation if server is run as root

## Summary
Severity: High
Advisory: GHSA-x7fr-pg8f-93f5
CVE: CVE-2023-1521
CWE: CWE-426
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-x7fr-pg8f-93f5
Type: github-advisory

## Affected
- crates.io: `sccache` — affected >=0 <0.4.0

## Details
### Impact

On Linux the `sccache` client can execute arbitrary code with the privileges of a local `sccache` server, by preloading the code in a shared library passed to `LD_PRELOAD`.

If the server is run as root (which is the default when installing the [snap package](https://snapcraft.io/sccache)), this means a user running the `sccache` client can get root privileges.


### Patches
Upgrade to 0.4.0

### Workarounds
Don't run sccache server as root. 

###  GitHub Security Lab number

GHSL-2023-046

## References
- https://github.com/mozilla/sccache/security/advisories/GHSA-x7fr-pg8f-93f5
- https://nvd.nist.gov/vuln/detail/CVE-2023-1521
- https://github.com/mozilla/sccache
- https://github.com/mozilla/sccache/releases/tag/v0.4.0
- https://securitylab.github.com/advisories/GHSL-2023-046_ScCache
