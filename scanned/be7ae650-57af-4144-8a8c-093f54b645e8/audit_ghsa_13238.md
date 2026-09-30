# [M] matrix-synapse vulnerable to improper validation of receipts allows forged read receipts

## Summary
Severity: Medium
Advisory: GHSA-7565-cq32-vx2x
CVE: CVE-2023-42453
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-26
Source: https://github.com/advisories/GHSA-7565-cq32-vx2x
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0.34.0 <1.93.0

## Details
### Impact
Users were able to forge read receipts for any event (if they knew the room ID and event ID). Note that the users were not able to view the events, but simply mark it as read. This could be confusing as clients will show the event as read by the user, even if they are not in the room.

### Patches
https://github.com/matrix-org/synapse/pull/16327

### Workarounds
There is no workaround.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-7565-cq32-vx2x
- https://nvd.nist.gov/vuln/detail/CVE-2023-42453
- https://github.com/matrix-org/synapse/pull/16327
- https://github.com/matrix-org/synapse/commit/63d28a88c1d18c64ea7e23b6dd7483e6d5dcf881
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2023-180.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2AFB2Y3S2VCPCN5P2XCZTG24MBMZ7DM4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/65QPC55I4D27HIZP7H2NQ34EOXHPP4AO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N6P4QULVUE254WI7XF2LWWOGHCYVFXFY
- https://security.gentoo.org/glsa/202401-12
