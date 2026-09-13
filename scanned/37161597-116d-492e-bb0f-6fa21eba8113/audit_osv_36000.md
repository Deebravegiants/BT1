# [M] Kong Mesh multi-zone: the global control plane attributes KDS-synced resources by an unvalidated in-band zone identifier

## Summary
Severity: Medium
Advisory: CVE-2026-18674
Aliases: GHSA-m58j-fjmc-h3g4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-18674
Type: osv

## Details
On a Kong Mesh global control plane, resources received over the zone-to-global KDS sync are attributed using the in-band, sender-controlled ControlPlane.Identifier rather than the authenticated zone identity derived from the connection. Authenticated zones can have the global control plane store and re-distribute those resources as belonging to another zone.



The result is a cross-zone isolation bypass: the holder of a single enrolled zone's credential can inject, attribute, and overwrite resources in another zone's namespace mesh-wide.




The root cause lives in Kuma's open-source KDS sync code, which Kong Mesh's control plane is built on.

## References
- https://developer.konghq.com/mesh/changelog/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18674.json
- https://github.com/kumahq/kuma/security/advisories/GHSA-m58j-fjmc-h3g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-18674
- https://github.com/kumahq/kuma/pull/17456
- https://github.com/kumahq/kuma/pull/17458
- https://github.com/kumahq/kuma/pull/17459
- https://github.com/kumahq/kuma/pull/17460
- https://github.com/kumahq/kuma/pull/17461
- https://github.com/kumahq/kuma/pull/17462
- https://github.com/kumahq/kuma/pull/17463
