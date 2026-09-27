# [M] Indico may disclose unauthorized user details access via legacy API

## Summary
Severity: Medium
Advisory: GHSA-4269-mcfh-cp7q
CVE: CVE-2025-59034
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-4269-mcfh-cp7q
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.8

## Details
### Impact
A legacy API to retrieve user details could be misused to retrieve profile details of other users without having admin permissions due to a broken access check.

### Patches
You should to update to [Indico 3.3.8](https://github.com/indico/indico/releases/tag/v3.3.8) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
It is possible to restrict access to the affected API (e.g. in the webserver config) which is most likely unused anyway and thus will not break anything.

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-4269-mcfh-cp7q
- https://nvd.nist.gov/vuln/detail/CVE-2025-59034
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.8
