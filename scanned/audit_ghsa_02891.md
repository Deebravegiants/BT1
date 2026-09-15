# [H] Path traversal in Matrix Synapse

## Summary
Severity: High
Advisory: GHSA-3hfw-x7gx-437c
CVE: CVE-2021-41281
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-3hfw-x7gx-437c
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.47.1

## Details
### Impact

Synapse instances with the media repository enabled can be tricked into downloading a file from a remote server into an arbitrary directory, potentially outside the media store directory.

The last two directories and file name of the path are chosen randomly by Synapse and cannot be controlled by an attacker, which limits the impact.

Homeservers with the media repository disabled are unaffected. Homeservers configured with a federation whitelist are also unaffected.

### Patches
Server administrators should upgrade to 1.47.1 or later.

### Workarounds
Server administrators using a reverse proxy could, at the expense of losing media functionality, block the following endpoints:

* `/_matrix/media/r0/download/{serverName}/{mediaId}`
* `/_matrix/media/r0/download/{serverName}/{mediaId}/{fileName}`
* `/_matrix/media/r0/thumbnail/{serverName}/{mediaId}`

Alternatively, non-containerized deployments can be adapted to use the hardened systemd config, located at `contrib/systemd/override-hardened.conf`.

### References
n/a

### For more information

If you have any questions or comments about this advisory, e-mail us at security@matrix.org.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-3hfw-x7gx-437c
- https://nvd.nist.gov/vuln/detail/CVE-2021-41281
- https://github.com/matrix-org/synapse/commit/91f2bd090
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.47.1
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-436.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EU7QRE55U4IUEDLKT5IYPWL3UXMELFAS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N3WY56LCEZ4ZECLWV5KMAXF2PSMUB4F2
