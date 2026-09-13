# [H]  Fission: Zip Slip in pkg/utils/zip.go:Unarchive allows fetcher to write outside the destination directory

## Summary
Severity: High
Advisory: GHSA-q6vm-xqc9-v3ff
CVE: CVE-2026-50567
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-q6vm-xqc9-v3ff
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.25.0

## Details
`Unarchive` in `pkg/utils/zip.go` joined each archive entry name with the destination directory via `filepath.Join` and wrote the result without checking whether the resolved path stayed under the destination. A zip entry named
  `../../tmp/evil` therefore landed at `/tmp/evil`. An attacker who could control a `Package.Spec.Source.URL` or `Deployment.URL` archive could induce the fetcher (running as the per-environment pod's `fission-fetcher` sidecar) to write
  files anywhere that process could reach: into other tenants' `/packages/<ns>/` directories, into mounted secret/config volumes, or into the fetcher's own binary.

  ### Affected

  - Project: `github.com/fission/fission`
  - Versions: all up to and including v1.24.0
  - Audited commit: `647c141`
  - Component: `pkg/utils/zip.go` (`Unarchive`)
  - Configuration: default; triggered when the fetcher downloads and extracts a zip archive

  Fix section (paste into the Fix / Patches field)

  Fixed in [v1.25.0](https://github.com/fission/fission/releases/tag/v1.25.0) by:

  - [PR #3444](https://github.com/fission/fission/pull/3444) (commit [`55704aca`](https://github.com/fission/fission/commit/55704aca1b8d6f45bc7c7c2e4805c7e14875ec0f)) — `Unarchive` now opens an `os.Root` on the destination, validates each
  archive entry name (rejects absolute paths and `..` traversal), and refuses symlink entries up front. The `os.Root` confines every `mkdir` / `create` to the destination in the kernel.

  Regression coverage: `TestUnarchiveZipSlip` in `pkg/utils/zip_test.go` exercises parent-traversal, absolute-path, and symlink entries.

## References
- https://github.com/fission/fission/security/advisories/GHSA-q6vm-xqc9-v3ff
- https://nvd.nist.gov/vuln/detail/CVE-2026-50567
- https://github.com/fission/fission/pull/3444
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.25.0
