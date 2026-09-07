# [M] Indico vulnerable to Cross-Site Scripting via LaTeX math code

## Summary
Severity: Medium
Advisory: GHSA-7cf7-9wrr-vrf4
CVE: CVE-2025-59035
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-7cf7-9wrr-vrf4
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.8

## Details
### Impact
There is a Cross-Site-Scripting vulnerability when rendering LaTeX math code in contribution or abstract descriptions. 

### Patches
You should to update to [Indico 3.3.8](https://github.com/indico/indico/releases/tag/v3.3.8) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
Only let trustworthy users create content on Indico.

Note that a conference doing a Call for Abstracts actively invites external speakers (who the organizers may not know and thus cannot fully trust) to submit content, hence the need to update to a a fixed version ASAP in particular when using such workflows.

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-7cf7-9wrr-vrf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-59035
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.8
