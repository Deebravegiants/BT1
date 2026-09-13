# [C] act 0.2.81 through 0.2.89 Missing Authorization in the Artifacts V4 Backend

## Summary
Severity: Critical
Advisory: CVE-2026-76847
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76847
Type: osv

## Details
act starts an HTTP Artifacts V4 backend whenever a workflow uses actions/upload-artifact@v4 or actions/download-artifact@v4. The control-plane RPCs of that backend, including CreateArtifact, GetSignedArtifactURL, ListArtifacts, FinalizeArtifact and DeleteArtifact, accept a caller-supplied workflow_run_backend_id and never check that it belongs to the requester: validateRunIDV4 in pkg/artifacts/artifacts_v4.go parses the value and returns it with the comparison against the requesting task's run ID left commented out. The signed URLs the backend issues are authenticated by an HMAC whose key is hardcoded to the four bytes 0xba 0xdb 0xee 0xf0, identical in every build, computed over a concatenation of endpoint, expiry, artifact name and task ID with no length prefix or delimiter, so signatures are both forgeable and ambiguous between differing artifact name and task ID pairs. The --artifact-server-addr flag defaults to the host's outbound address rather than loopback, leaving the backend reachable from the surrounding network. Any client that can reach it may read, overwrite or delete the artifacts of a concurrently running job with no credentials, exposing build outputs such as secrets and deployment credentials and permitting their replacement before the owning job consumes them.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76847.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76847
- https://www.vulncheck.com/advisories/act-through-missing-authorization-in-the-artifacts-v4-backend
- https://github.com/nektos/act
- https://github.com/nektos/act/blob/v0.2.89/cmd/root.go
- https://github.com/nektos/act/blob/v0.2.89/pkg/artifacts/artifacts_v4.go
