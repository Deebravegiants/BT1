# [M] Indico has a missing access check in the event series management API

## Summary
Severity: Medium
Advisory: GHSA-rfpp-2hgm-gp5v
CVE: CVE-2026-28352
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-rfpp-2hgm-gp5v
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.11

## Details
### Impact
The API endpoint used to manage event series is missing an access check, allowing unauthenticated/unauthorized access to this endpoint.

The impact of this is limited to:

- Getting the metadata (title, category chain, start/end date) for events in an existing series
- Deleting an existing event series: This just removes the series metadata, ie (if enabled) the links between events in the same series and the lecture series number in the event title
- Modifying an existing event series: Just like for deleting, it would only allow to toggle the metadata display. It could also be used to set an event title pattern for the series, but this is only used when cloning an event from that series.

That this vulnerability does NOT allow unauthorized access to events (beyond the basic metadata mentioned above), nor any kind of tampering with user-visible data in events.

### Patches
Developers should to update to [Indico 3.3.11](https://github.com/indico/indico/releases/tag/v3.3.11) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
- Developers can configure their webserver to restrict access to the series management API endpoint

### For more information
If there are any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email Indico privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-rfpp-2hgm-gp5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-28352
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.11
