# [H] Previous ATX is not checked to be the newest valid ATX by Smesher when validating incoming ATX

## Summary
Severity: High
Advisory: GHSA-jcqq-g64v-gcm7
CVE: CVE-2024-34360
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-05-10
Source: https://github.com/advisories/GHSA-jcqq-g64v-gcm7
Type: github-advisory

## Affected
- Go: `github.com/spacemeshos/go-spacemesh` — affected >=0 <1.5.2-hotfix1
- Go: `github.com/spacemeshos/api` — affected >=0 <1.37.1

## Details
### Impact
Nodes can publish ATXs which reference the incorrect previous ATX of the Smesher that created the ATX. ATXs are expected to form a single chain from the newest to the first ATX ever published by an identity. Allowing Smeshers to reference an earlier (but not the latest) ATX as previous breaks this protocol rule and can serve as an attack vector where Nodes are rewarded for holding their PoST data for less than one epoch but still being eligible for rewards.

### Patches
- API needs to be extended to be able to fetch events from a node that dected malicious behavior of this regard by the node
- go-spacemesh needs to be patched to a) not allow publishing these ATXs any more and b) create malfeasance proofs for identities that published invalid ATXs in the past.

### Workarounds
n/a

### References
Spacemesh protocol whitepaper: https://spacemesh.io/blog/spacemesh-white-paper-1/, specifically sections 4.4.2 ("ATX Contents") and 4.4.3 ("ATX validity")

## References
- https://github.com/spacemeshos/go-spacemesh/security/advisories/GHSA-jcqq-g64v-gcm7
- https://nvd.nist.gov/vuln/detail/CVE-2024-34360
- https://github.com/spacemeshos/api/commit/1d5bd972bbe225d024c3e0ae5214ddb6b481716e
- https://github.com/spacemeshos/go-spacemesh/commit/9aff88d54be809ac43d60e8a8b4d65359c356b87
- https://github.com/spacemeshos/go-spacemesh
- https://pkg.go.dev/vuln/GO-2024-2831
- https://spacemesh.io/blog/spacemesh-white-paper-1
