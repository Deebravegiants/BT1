# [H] whoami stack buffer overflow on several Unix platforms

## Summary
Severity: High
Advisory: GHSA-w5w5-8vfh-xcjq
CWE: CWE-121
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-w5w5-8vfh-xcjq
Type: github-advisory

## Affected
- crates.io: `whoami` — affected >=0.5.3 <1.5.0

## Details
With versions of the whoami crate >= 0.5.3 and < 1.5.0, calling any of these functions leads to an immediate stack buffer overflow on illumos and Solaris:

- `whoami::username`
- `whoami::realname`
- `whoami::username_os`
- `whoami::realname_os`

With versions of the whoami crate >= 0.5.3 and < 1.0.1, calling any of the above functions also leads to a stack buffer overflow on these platforms:

- Bitrig
- DragonFlyBSD
- FreeBSD
- NetBSD
- OpenBSD

This occurs because of an incorrect definition of the `passwd` struct on those platforms.

As a result of this issue, denial of service and data corruption have both been observed in the wild. The issue is possibly exploitable as well.

This vulnerability also affects other Unix platforms that aren't Linux or macOS.

This issue has been addressed in whoami 1.5.0.

For more information, see [this GitHub issue](https://github.com/ardaku/whoami/issues/91).

## References
- https://github.com/ardaku/whoami/issues/91
- https://github.com/ardaku/whoami/commit/d6ee13ed9e818aa51b8d86d95e8009a376289a40
- https://github.com/ardaku/whoami
- https://rustsec.org/advisories/RUSTSEC-2024-0020.html
