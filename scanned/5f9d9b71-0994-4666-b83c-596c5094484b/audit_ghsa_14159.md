# [H] Synapse Denial of service due to incorrect application of event authorization rules during state resolution

## Summary
Severity: High
Advisory: GHSA-p9qp-c452-f9r7
CVE: CVE-2022-39374
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-p9qp-c452-f9r7
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=1.62.0 <1.68.0rc1

## Details
### Impact
If Synapse and a malicious homeserver are both joined to the same room, the malicious homeserver can trick Synapse into accepting previously rejected events into its view of the current state of that room. This can be exploited in a way that causes all further messages and state changes sent in that room from the vulnerable homeserver to be rejected.

Synapse homeservers are affected by this issue if and only if they are joined to rooms which members of untrusted homeservers are joined or invited to. 

- Synapse homeservers in rooms available over public federation **are** affected.
- Synapse homeservers with federation disabled are not affected.
- Synapse homeservers in a closed federation containing only trusted servers are not affected.
- Synapse homeservers which are only joined to rooms with federation disabled[^1] are not affected.

### Patches
Administrators of homeservers with federation enabled are advised to upgrade to 1.68.0 or higher.

### Workarounds
 * Federation can be disabled by setting [`federation_domain_whitelist`](https://matrix-org.github.io/synapse/latest/usage/configuration/config_documentation.html#federation_domain_whitelist) to an empty list (`[]`). from the vulnerable homeserver to be rejected. This issue has been patched in version 1.68.0

### References
- https://github.com/matrix-org/synapse/pull/13723

[^1]: See `m.federate` in the [`m.room.create` definition](https://spec.matrix.org/v1.4/client-server-api/#mroomcreate).

### For more information

If you have any questions or comments about this advisory, e-mail us at [security@matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-p9qp-c452-f9r7
- https://nvd.nist.gov/vuln/detail/CVE-2022-39374
- https://github.com/matrix-org/synapse/pull/13723
- https://github.com/matrix-org/synapse/commit/b73cbb82157d9666e8d667733afebc0d09ed858c
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2023-66.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UJIJRP5ZH6B3KGFLHCAKR2IX2Y4Z25QD
