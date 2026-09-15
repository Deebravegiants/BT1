# [M] CVE-2021-21394

## Summary
Severity: Medium
Advisory: CVE-2021-21394
Aliases: GHSA-w9fg-xffh-p362, PYSEC-2021-27
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-12
Source: https://osv.dev/vulnerability/CVE-2021-21394
Type: osv

## Details
Synapse is a Matrix reference homeserver written in python (pypi package matrix-synapse). Matrix is an ecosystem for open federated Instant Messaging and VoIP. In Synapse before version 1.28.0 Synapse is missing input validation of some parameters on the endpoints used to confirm third-party identifiers could cause excessive use of disk space and memory leading to resource exhaustion. Note that the groups feature is not part of the Matrix specification and the chosen maximum lengths are arbitrary. Not all clients might abide by them. Refer to referenced GitHub security advisory for additional details including workarounds.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY/
- https://github.com/matrix-org/synapse/pull/9321
- https://github.com/matrix-org/synapse/pull/9393
- https://github.com/matrix-org/synapse/security/advisories/GHSA-w9fg-xffh-p362
- https://pypi.org/project/matrix-synapse/
