# [M] Synapse Outgoing federation to specific hosts can be disabled by sending malicious invites

## Summary
Severity: Medium
Advisory: GHSA-f3wc-3vxv-xmvr
CVE: CVE-2023-32323
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-f3wc-3vxv-xmvr
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.74.0

## Details
### Impact

A malicious user on a Synapse homeserver X with permission to create certain state events can disable outbound federation from X to an arbitrary homeserver Y.

Synapse instances with federation disabled are not affected.

#### Details

The Matrix protocol allows homeservers to provide an `invite_room_state` field on a [room invite](https://spec.matrix.org/v1.5/client-server-api/#mroommember) containing a [summary of room state](https://spec.matrix.org/v1.5/client-server-api/#stripped-state).  In versions of Synapse up to and including v1.73.0, Synapse did not limit the size of `invite_room_state`, meaning that it was possible to create an arbitrarily large invite event.

An attacker with an account on a vulnerable Synapse homeserver X could exploit this by having X create an over-sized invite event in a room with a user from another homeserver Y. Once acknowledged by the invitee's homeserver, the invite event would be sent in a batch of events to Y. If the malicious invite is so large that the entire batch is rejected as too large, X's outgoing traffic to Y would become "stuck", meaning that messages and state events created by X would remain unseen by Y.

### Patches

Synapse 1.74 refuses to create oversized `invite_room_state` fields. Server operators should upgrade to Synapse 1.74 or newer urgently.

### Workarounds

There are no robust workarounds.

This attack needs an account on Synapse homeserver X to deny federation from X to another homeserver Y. As a partial mitigation, Synapse operators can disable open registration to limit the ability of attackers to create new accounts on homeserver X.

If homeserver X has been attacked in this way, restarting it will resume outgoing federation by entering "catchup mode". For catchup mode to ignore the oversized invites, every attacked room must have a correctly-sized event sent by X which is newer than any oversized invite. This is difficult to arrange, and does not prevent the attacker from repeating their attack.

### References

- https://github.com/matrix-org/synapse/issues/14492 was caused by this issue.
- https://github.com/matrix-org/synapse/issues/14642  includes the patch described above.

### For more information

If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-f3wc-3vxv-xmvr
- https://nvd.nist.gov/vuln/detail/CVE-2023-32323
- https://github.com/matrix-org/synapse/issues/14492
- https://github.com/matrix-org/synapse/pull/14642
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2023-67.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UJIJRP5ZH6B3KGFLHCAKR2IX2Y4Z25QD
