# [M] snapd failed to restrict writes to the $HOME/bin path

## Summary
Severity: Medium
Advisory: GHSA-4mh8-9689-38vr
CVE: CVE-2024-1724
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-25
Source: https://github.com/advisories/GHSA-4mh8-9689-38vr
Type: github-advisory

## Affected
- Go: `github.com/snapcore/snapd` — affected >=0 <2.62

## Details
In snapd versions prior to 2.62, when using AppArmor for enforcement of sandbox permissions, snapd failed to restrict writes to the $HOME/bin path. In Ubuntu, when this path exists, it is automatically added to the users PATH. An attacker who could convince a user to install a malicious snap which used the 'home' plug could use this vulnerability to install arbitrary scripts into the users PATH which may then be run by the user outside of the expected snap sandbox and hence allow them to escape confinement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1724
- https://github.com/snapcore/snapd/pull/13689
- https://github.com/snapcore/snapd/commit/aa191f97713de8dc3ce3ac818539f0b976eb8ef6
- https://github.com/snapcore/snapd
- https://gld.mcphail.uk/posts/explaining-cve-2024-1724
- https://pkg.go.dev/vuln/GO-2024-3007
