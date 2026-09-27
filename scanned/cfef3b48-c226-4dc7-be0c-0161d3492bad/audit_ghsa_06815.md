# [H] goshs: File-based .goshs ACL authorization bypass via the ?bulk zip-download route (unauthenticated read; residual of GHSA-wvhv-qcqf-f3cx)

## Summary
Severity: High
Advisory: GHSA-rmxw-pq4x-3fvh
CVE: CVE-2026-54719
CWE: CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-rmxw-pq4x-3fvh
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs` — affected >=0
- Go: `github.com/patrickhener/goshs/v2` — affected >=0 <2.1.1
- Go: `goshs.de/goshs` — affected >=0
- Go: `goshs.de/goshs/v2` — affected >=0 <2.1.1

## Details
GHSA-wvhv-qcqf-f3cx fixed the per-folder .goshs ACL bypass on the state-changing routes (PUT/POST upload/?mkdir/?delete) and added recursive ACL resolution, and its description states the read/list path correctly enforces .goshs. That premise does not hold for the ?bulk zip-download route. bulkDownload (httpserver/updown.go) takes one or more ?file= parameters, runs each through sanitizePath(fs.Webroot, file), and streams the contents back as a ZIP without ever calling findEffectiveACL/applyCustomAuth. It is dispatched from earlyBreakParameters (?bulk) before the normal doDir/doFile/sendFile flow that performs the ACL check. An unauthenticated attacker can therefore read any file under the webroot protected solely by a .goshs ACL, bypassing both the folder auth (401 on the normal path) and the per-file block list (404 on the normal path). Same authorization-inconsistency root cause as the original advisory, surviving on a read route the fix did not cover.

Proof of concept (live, against the fixed v2.1.0 build which includes fix commit f212c4f4, served with no global -b auth, only a per-folder .goshs):
  GET /protected/secret.txt              -> 401 (ACL enforced on normal path)
  GET /protected/secret.txt -u admin:admin -> 200
  GET /?bulk&file=/protected/secret.txt  -> 200, zip contains the protected file contents  (BYPASS)
  GET /?bulk&file=/protected/blocked.txt -> 200, zip contains the block-listed file        (block bypass)
  GET /protected/secret.txt?share        -> 403 'Sharing disabled when auth is disabled'    (correctly gated, NOT a bypass)

Impact: any unauthenticated network attacker can read files an operator protected with the documented per-folder .goshs ACL/basic-auth feature, by requesting them through ?bulk. Confidentiality only (the write/delete equivalents were closed by GHSA-wvhv-qcqf-f3cx). Applies to deployments relying on .goshs as the access boundary (a server-wide -b basic auth, if configured, also gates ?bulk via its middleware).

Remediation: enforce the effective .goshs ACL inside bulkDownload for every requested file exactly as sendFile/processDir do (resolve findEffectiveACL(filepath.Dir(absPath)) + applyCustomAuth + honor acl.Block), or route ?bulk through the same authorization gate as the normal read path. Audit ?cbDown and other alternate read routes for the same gap.

Credit: anir0y (independent security research).

## References
- https://github.com/goshs-labs/goshs/security/advisories/GHSA-rmxw-pq4x-3fvh
- https://github.com/goshs-labs/goshs/commit/7cf911a26ace737e1a55b7dc073e307a25f7fd1d
- https://github.com/goshs-labs/goshs
- https://github.com/goshs-labs/goshs/releases/tag/v2.1.1
