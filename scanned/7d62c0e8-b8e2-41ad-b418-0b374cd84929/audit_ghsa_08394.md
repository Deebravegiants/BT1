# [M] astral-tokio-tar has a PAX Header Desynchronization issue

## Summary
Severity: Medium
Advisory: GHSA-3cv2-h65g-fgmm
CWE: CWE-20, CWE-843
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-3cv2-h65g-fgmm
Type: github-advisory

## Affected
- crates.io: `astral-tokio-tar` — affected >=0 <0.6.2

## Details
### Impact

Versions of astral-tokio-tar prior to 0.6.2 contain a PAX header interpretation bug that allows manipulated entries to be made selectively visible or invisible during extraction with astral-tokio-tar versus other tar implementations. An attacker could use this differential to smuggle unexpected files onto a victim's filesystem.

### Details

When a tar stream contains multiple "header" entries prior to a file entry, astral-tokio-tar applies the PAX header (`x`) to the next entry in the stream, regardless of type. For example, a stream of `x -> L -> file` (PAX, GNU longname, file) would result in `x`'s extensions being applied to `L` rather than to `file`.

[Per POSIX pax](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/pax.html), this is incorrect: a PAX header always applies to a file entry, not any intermediary entries. See the "pax Header Block" section for the specific prescription there.

As a result of this, an attacker can contrive a tar containing a sequence of tar headers such that astral-tokio-tar applies the PAX header's size extension to the next header in sequence, effectively desynchronizing the stream and enabling astral-tokio-tar specific skippage/extraction of members. In other words, a file can be contrived to extract differently on astral-tokio-tar than on other tar parsers.

### Patches

Versions 0.6.2 and newer of astral-tokio-tar address this differential.

### Workarounds

Users are advised to upgrade to version 0.6.1 or newer to address this advisory.

There is no workaround other than upgrading. Users should experience no breaking changes as a result of the upgrade.

### Resources

- GHSA-j5gw-2vrg-8fgx is a similar PAX desynchronization bug
- GHSA-fp55-jw48-c537 is another similar PAX desynchronization bug

## References
- https://github.com/astral-sh/tokio-tar/security/advisories/GHSA-3cv2-h65g-fgmm
- https://github.com/astral-sh/tokio-tar
- https://rustsec.org/advisories/RUSTSEC-2026-0145.html
