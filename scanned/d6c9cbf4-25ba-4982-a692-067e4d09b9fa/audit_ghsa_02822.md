# [H] Authentication Bypass Using an Alternate Path or Channel and Authentication Bypass by Primary Weakness in rucio-webui

## Summary
Severity: High
Advisory: GHSA-v988-828w-xvf2
CWE: CWE-288, CWE-305
Ecosystem: PyPI
Published: 2021-10-22
Source: https://github.com/advisories/GHSA-v988-828w-xvf2
Type: github-advisory

## Affected
- PyPI: `rucio-webui` — affected >=1.26.0 <1.26.7

## Details
### Impact
`rucio-webui` installations of the `1.26` release line potentially leak the contents of cookies to other sessions within a wsgi container. Impact is that Rucio authentication tokens are leaked to other users accessing the `webui` within a close timeframe, thus allowing users to access the `webui` with the leaked authentication token. Privileges are therefore also escalated.

Rucio server / daemons are not affected by this issue, it is isolated to the webui.

### Patches
This issue is fixed in the `1.26.7` release of the `rucio-webui`.

### Workarounds
Installation of the `1.25.7` `webui` release. The `1.25` and previous webui release lines are not affected by this issue.

### References
https://github.com/rucio/rucio/issues/4928

## References
- https://github.com/rucio/rucio/security/advisories/GHSA-v988-828w-xvf2
- https://github.com/rucio/rucio/issues/4810
- https://github.com/rucio/rucio/issues/4928
- https://github.com/rucio/rucio/commit/8f832404ae88d6300e17d7e706b40fe58e0df90c
- https://github.com/rucio/rucio
- https://github.com/rucio/rucio/releases/tag/1.26.7
