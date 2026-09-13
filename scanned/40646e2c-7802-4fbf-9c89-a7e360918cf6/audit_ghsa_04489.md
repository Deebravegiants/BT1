# [M] RabbitMQ has predictable credential obfuscation seed value used in Shovel and Federation plugins

## Summary
Severity: Medium
Advisory: GHSA-v9gv-xp36-jgj8
CVE: CVE-2022-31008
CWE: CWE-330, CWE-335
Ecosystem: Hex
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-v9gv-xp36-jgj8
Type: github-advisory

## Affected
- Hex: `rabbit_common` — affected >=3.10.0 <3.10.2
- Hex: `rabbit_common` — affected >=3.9.0 <3.9.18
- Hex: `rabbit_common` — affected >=3.8.0 <3.8.32

## Details
### Impact

Shovel and Federation plugins perform URI obfuscation in their worker (link) state. The encryption key used to encrypt
the URI was seeded with a predictable secret.

This means that in case of certain exceptions related to Shovel and Federation plugins,
reasonably easily deobfuscatable data could appear in the node log.

Patched versions correctly use a cluster-wide secret for that purpose.

### Patches

Patched versions:

 * `3.10.2`
 * `3.9.18`
 * `3.8.32`

### Workarounds

Disable Shovel and Federation plugins.

### Credits

RabbitMQ core team would like to thank Lajos @luos Gerecs and Anh Nguyen from Erlang Solutions
for responsibly disclosing and working with us on a patch for this vulnerability.

### For more information

 * [Mailing list](https://groups.google.com/forum/#!forum/rabbitmq-users)
 * [Community Slack](https://rabbitmq-slack.herokuapp.com/)

## References
- https://github.com/rabbitmq/rabbitmq-server/security/advisories/GHSA-v9gv-xp36-jgj8
- https://nvd.nist.gov/vuln/detail/CVE-2022-31008
- https://github.com/rabbitmq/rabbitmq-server/pull/4841
- https://github.com/rabbitmq/rabbitmq-server/commit/c22e1cb20e656d211e025c417d1fc75a9067b717
- https://github.com/rabbitmq/rabbitmq-server
