# [H] Synapse does not apply enough checks to servers requesting auth events of events in a room

## Summary
Severity: High
Advisory: GHSA-45cj-f97f-ggwv
CVE: CVE-2022-39335
CWE: CWE-200, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-45cj-f97f-ggwv
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.69.0

## Details
### Impact
Synapse is an open-source Matrix homeserver written and maintained by the Matrix.org Foundation. The Matrix Federation API allows remote homeservers to request the *authorisation events* of events in a room. This is necessary so that a homeserver receiving some events can validate that those events are legitimate and permitted in their room.
However, in versions of Synapse up to and including 1.68.0, a Synapse homeserver answering a query for authorisation events does not sufficiently check that the requesting server should be able to access them.

Authorisation events include power level events (the list of user IDs and their power levels at the time) and relevant membership events (including the display name of the sender of that event), as well as events like `m.room.create`, `m.room.third_party_invite` and `m.room.join_rules`. Non-authorisation events are unaffected, so it isn't possible to e.g. extract message contents this way.

This issue is only exploitable when a malicious actor knows the ID of a target room and the ID of an event from that room. In most cases, this makes exploitation infeasible. This issue is of negligible consequence for public rooms given that any server can easily join the room in order to be allowed to view authorisation events. Further, deployments in a closed federation where all homeservers are trustworthy are not affected.


### Patches

The issue was patched in Synapse 1.69.0. Homeserver administrators are advised to upgrade.


### Workarounds

Synapse can be configured with a list of servers that it is allowed to federate with [`federation_domain_whitelist`]. If this list is in use and all the servers on the list are trusted not to exploit this issue, then this issue is of no consequence.

This workaround is not practical for homeservers participating in open federation as interaction with any server not on the list would have to happen indirectly through servers that are, leading to inconsistent delays in message delivery.

[`federation_domain_whitelist`]: https://matrix-org.github.io/synapse/v1.68/usage/configuration/config_documentation.html#federation_domain_whitelist

### References

Fixed in https://github.com/matrix-org/synapse/pull/13823.


### For more information

If you have any questions or comments about this advisory, e-mail us at security@matrix.org.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-45cj-f97f-ggwv
- https://nvd.nist.gov/vuln/detail/CVE-2022-39335
- https://github.com/matrix-org/synapse/issues/13288
- https://github.com/matrix-org/synapse/pull/13823
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2023-65.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T2MBNMZAFY4RCZL2VGBGAPKGB4JUPZVS
