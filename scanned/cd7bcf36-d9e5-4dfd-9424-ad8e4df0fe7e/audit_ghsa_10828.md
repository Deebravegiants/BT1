# [M] astral-tokio-tar insufficiently validates PAX extensions during extraction

## Summary
Severity: Medium
Advisory: GHSA-6gx3-4362-rf54
CVE: CVE-2026-32766
CWE: CWE-436
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-6gx3-4362-rf54
Type: github-advisory

## Affected
- crates.io: `astral-tokio-tar` — affected >=0 <0.6.0

## Details
## Impact

In versions 0.5.6 and earlier of astral-tokio-tar, malformed PAX extensions were silently skipped when parsing tar archives. This silent skipping (rather than rejection) of invalid PAX extensions could be used as a building block for a parser differential, for example by having astral-tokio-tar silently skip a malformed GNU “long link” extension so that a subsequent parser would misinterpret the extension.

In practice, exploiting this behavior in astral-tokio-tar requires a secondary misbehaving tar parser, i.e. one that insufficiently validates malformed PAX extensions and interprets them rather than skipping or erroring on them. Consequently this advisory is considered low-severity within astral-tokio-tar itself, as it requires a separate vulnerability against any unrelated tar parser.

## Patches

Versions 0.6.0 and newer of astral-tokio-tar reject invalid PAX extensions, rather than silently skipping them. 

## Workarounds

Users are advised to upgrade to version 0.6.0 or newer to address this advisory.

Most users should experience no breaking changes as a result of the patch above. Some users who attempt to extract poorly constructed tar files may experience errors; users should re-construct their tar files with a conforming tar parser.

## Attribution

- Sergei Zimmerman (@xokdvium)

## References
- https://github.com/astral-sh/tokio-tar/security/advisories/GHSA-6gx3-4362-rf54
- https://nvd.nist.gov/vuln/detail/CVE-2026-32766
- https://github.com/astral-sh/tokio-tar/commit/e5e0139cae4577eeedf5fc16b65e690bf988ce52
- https://github.com/astral-sh/tokio-tar
- https://rustsec.org/advisories/RUSTSEC-2026-0066.html
