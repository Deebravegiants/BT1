# [H] Denial of service attack due to invalid JSON

## Summary
Severity: High
Advisory: GHSA-4mp3-385r-v63f
CVE: CVE-2020-26890
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-11-24
Source: https://github.com/advisories/GHSA-4mp3-385r-v63f
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.20.0

## Details
### Impact
A denial of service attack against Matrix clients can be exploited by sending an event including invalid JSON data to Synapse. Synapse would relay the data to clients which could crash or hang. Impact is long-lasting if the event is made part of the room state.

### Patches
At a minimum #8106 and #8291 must be applied. #7372 and #8124 include additional checks.

### Workarounds
There are no known workarounds.

### Upgrading notes
If an invalid event is accepted by an earlier Synapse it can become part of the room state and will not be fixed by upgrading Synapse. Redacting the invalid event should avoid clients receiving the invalid event.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-4mp3-385r-v63f
- https://nvd.nist.gov/vuln/detail/CVE-2020-26890
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2020-237.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G7YXMMYQP46PYL664JQUXCA3LPBJU7DQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U34DPP4ZLOEDUY2ZCWOHQPU5GA5LYNUQ
- https://pypi.org/project/matrix-synapse
