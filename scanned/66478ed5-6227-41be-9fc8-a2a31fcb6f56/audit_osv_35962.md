# [M] undici vulnerable to Denial of Service via orphaned RetryHandler response body

## Summary
Severity: Medium
Advisory: CVE-2026-18149
Aliases: GHSA-pmjh-fq2x-6v4x
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-18149
Type: osv

## Details
undici's retry handler can leave an already-exposed response body pending forever. When a server returns a successful response that declares a Content-Length, sends only part of the body, and closes the connection, the retry handler retries the request. If the retry returns a non-retryable status such as 400, the handler forwards that new response downstream and replaces its internal response stream, but the original response body that the application still holds is never ended or destroyed. As a result calls that read that body never settle, and the configured body timeout does not fire because its timer is tied to the connection parser rather than the orphaned body. An attacker-controlled server can trigger this with two short responses without keeping a connection open, and repeated requests accumulate pending promises and streams that can exhaust application concurrency or memory. This affects undici versions from 7.11.0 up to 7.29.1 and from 8.0.0 up to 8.10.2. Users should upgrade to undici 7.29.1 or 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18149.json
- https://github.com/nodejs/undici/security/advisories/GHSA-pmjh-fq2x-6v4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-18149
