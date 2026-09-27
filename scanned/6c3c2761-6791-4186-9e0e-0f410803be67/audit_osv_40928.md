# [M] Capgo - Cross-App Build Job Access via app_id/job_id Mismatch in /build/status and /build/logs

## Summary
Severity: Medium
Advisory: CVE-2026-56229
Aliases: GHSA-2fw5-mcrx-wcqw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56229
Type: osv

## Details
Capgo before 12.128.2 contains an authorization bypass vulnerability in the /build/status and /build/logs endpoints that allows attackers to access build jobs belonging to different applications by supplying a mismatched app_id and job_id combination. Limited API keys restricted to a single app can retrieve build status and logs from other apps by providing an authorized app_id while using a job_id from an unauthorized app, exposing sensitive build information including logs, metadata, and potentially credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56229.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-2fw5-mcrx-wcqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-56229
- https://www.vulncheck.com/advisories/capgo-cross-app-build-job-access-via-app-id-job-id-mismatch-in-build-status-and-build-logs
