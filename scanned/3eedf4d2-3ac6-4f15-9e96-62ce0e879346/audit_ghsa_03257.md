# [H] Legacy Node API Allows Impersonation in github.com/spiffe/spire/pkg/server/endpoints/node

## Summary
Severity: High
Advisory: GHSA-h746-rm5q-8mgq
CVE: CVE-2021-27098
CWE: CWE-284, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-h746-rm5q-8mgq
Type: github-advisory

## Affected
- Go: `github.com/spiffe/spire` — affected >=0.8.1 <0.8.5
- Go: `github.com/spiffe/spire` — affected >=0.9.0 <0.9.4
- Go: `github.com/spiffe/spire` — affected >=0.10.0 <0.10.2
- Go: `github.com/spiffe/spire` — affected >=0.11.0 <0.11.3
- Go: `github.com/spiffe/spire` — affected >=0.12.0 <0.12.1

## Details
#### Summary
In SPIRE 0.8.1 through 0.8.4 and before versions 0.9.4, 0.10.2, 0.11.3 and 0.12.1, specially crafted requests to the FetchX509SVID RPC of SPIRE Server’s Legacy Node API (github.com/spiffe/spire/pkg/server/endpoints/node) can result in the possible issuance of an X.509 certificate with a URI SAN for a SPIFFE ID that the agent is not authorized to distribute. Proper controls are in place to require that the caller presents a valid agent certificate that is already authorized to issue at least one SPIFFE ID, and the requested SPIFFE ID belongs to the same trust domain, prior to being able to trigger this vulnerability. This issue has been fixed in SPIRE versions 0.8.5, 0.9.4, 0.10.2, 0.11.3 and 0.12.1.

#### What are the changes introduced by the patched versions?
The changes introduced to address this issue are related to enforcing that the FetchX509SVID RPC of SPIRE Server’s Legacy Node API only issues X.509 certificates with SPIFFE IDs that the agent is authorized to distribute.

The patched version also includes a back-ported change that improves the handling of file descriptors related to workload attestation in SPIRE Agent.

There are no changes in the expected behavior of SPIRE.

#### Should I upgrade SPIRE?
All SPIRE users running affected versions are advised to upgrade to the corresponding patched version.

#### Workarounds
No workarounds have been identified for this vulnerability.

## References
- https://github.com/spiffe/spire/security/advisories/GHSA-h746-rm5q-8mgq
- https://nvd.nist.gov/vuln/detail/CVE-2021-27098
- https://github.com/spiffe/spire/commit/3c5115b57afc20a0a2c2b1b9dd60dd1fd9082e13
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-27098
