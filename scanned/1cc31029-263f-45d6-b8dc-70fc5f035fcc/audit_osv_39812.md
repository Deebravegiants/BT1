# [H] MeltanoHub vulnerable to command injection in the `test_dispatcher` GitHub Actions workflow

## Summary
Severity: High
Advisory: CVE-2026-47690
Aliases: GHSA-wrpf-f35c-j28w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47690
Type: osv

## Details
MeltanoHub is the source code for hub.meltano.com, the central place for Meltano plugins. Versions of the repo prior to commit 923820de8f64d753951fbbd54f7282a3d5f75173 were vulnerable to exfiltration of `GITHUB_TOKEN` with write permissions to the repository. The vulnerable workflow used pull_request_target, which runs in the context of the base repository with access to secrets. Commit 923820de8f64d753951fbbd54f7282a3d5f75173 fixes the issue. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47690.json
- https://github.com/meltano/hub/security/advisories/GHSA-wrpf-f35c-j28w
- https://nvd.nist.gov/vuln/detail/CVE-2026-47690
- https://github.com/meltano/hub/commit/923820de8f64d753951fbbd54f7282a3d5f75173
- https://github.com/meltano/hub/pull/2247
- https://github.com/meltano/hub/pull/2249
- https://github.com/meltano/hub/pull/2251
- https://github.com/myogahunter/meltano-hub-poc
