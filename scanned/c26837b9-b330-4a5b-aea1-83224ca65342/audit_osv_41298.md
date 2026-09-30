# [H] Insufficient verification of Hex package metadata in Gleam

## Summary
Severity: High
Advisory: CVE-2026-59247
Aliases: EEF-CVE-2026-59247, GHSA-4vvc-458m-r82g
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-59247
Type: osv

## Details
Insufficient Verification of Data Authenticity vulnerability in Gleam allows an adversary in the middle to substitute forged Hex package contents during dependency resolution.

During dependency resolution Gleam fetches package metadata from the signature-verified Hex repository, which covers each release's dependency requirements and SHA-256 outer_checksum. After resolving versions, gleam_cli::dependencies::lookup_package makes a second request to the unsigned Hex API through gleam_core::hex::get_package_release and records the outer_checksum and dependency names from that JSON response into manifest.toml, instead of the values from the verified repository metadata. The Hex repository signature does not cover the API response.

An adversary in the middle who can intercept TLS with a certificate trusted by the Gleam process (for example a TLS-inspecting proxy using a CA in the operating system trust store or added through GLEAM_CACERTS_PATH), and who can modify both the API release response and the corresponding repository tarball, can supply a package archive with a matching forged checksum without the Hex repository signing key. Gleam verifies the forged tarball against the forged checksum, accepts it, and extracts it as a dependency source, resulting in loss of integrity of the downloaded package contents.

Only projects that resolve or update Hex dependencies are affected, which happens when the manifest is missing, a dependency is added or updated, or dependency requirements change. Builds that reuse an unchanged, known-good manifest.toml continue to verify tarballs against its pinned checksum. This issue affects gleam: from 0.18.0 before 1.18.0.

## References
- https://cna.erlef.org/cves/CVE-2026-59247.html
- https://ghcr.io
- https://github.com
- https://github.com/hexpm/specifications/blob/main/registry-v2.md
- https://gleam.run
- https://osv.dev/vulnerability/EEF-CVE-2026-59247
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59247.json
- https://github.com/gleam-lang/gleam/security/advisories/GHSA-4vvc-458m-r82g
- https://nvd.nist.gov/vuln/detail/CVE-2026-59247
- https://github.com/gleam-lang/gleam/commit/c9c0d48c123c8abae6db8dd61b25ccb427ed3d35
- https://github.com/gleam-lang/gleam
