# [M] Cri-o: cri-o: unvalidated image env var causes daemon crash

## Summary
Severity: Medium
Advisory: CVE-2026-17113
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-17113
Type: osv

## Details
A flaw was found in CRI-O's container-creation environment-variable handling
(`mergeEnvs` in `server/utils.go`, consumed by `setupContainerEnvironmentAndWorkdir` in
`server/container_create.go`). When a `CreateContainer` request supplies a `nil` CRI
`Envs` field, CRI-O falls back to using the target OCI image's `config.Env` entries
unfiltered, in contrast to the normal merge path, which validates each entry for a
`key=value` form before use. An OCI image whose `config.Env` contains an entry with no
`=` character (e.g. a bare `NOEQUALS` string) causes CRI-O to split that entry into a
single-element slice and then index its second element, which is out of range. This
triggers an unrecovered Go runtime panic in the `crio` daemon process, crashing it and
terminating the container-runtime service for all workloads on the node until it is
restarted.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-17113
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17113
- https://bugzilla.redhat.com/show_bug.cgi?id=2506872
- https://github.com/cri-o/cri-o
