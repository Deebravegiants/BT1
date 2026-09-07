# [M] podinfo: cross-site scripting vulnerability in the /echo and /api/echo endpoints

## Summary
Severity: Medium
Advisory: GHSA-q23m-vm9r-5745
CVE: CVE-2026-43644
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-q23m-vm9r-5745
Type: github-advisory

## Affected
- Go: `github.com/stefanprodan/podinfo` — affected >=0 <1.8.1-0.20260519111337-cbebb20fd485

## Details
podinfo through 6.11.2 contains a reflected cross-site scripting vulnerability in the /echo and /api/echo endpoints where the echoHandler writes request body content directly to the response without setting explicit Content-Type or X-Content-Type-Options headers. Attackers can craft cross-origin HTML pages with auto-submitting forms containing script payloads in the request body, which are served as text/html due to Go's content type detection, allowing the reflected script to execute in the podinfo origin context when victims visit the attacker's page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43644
- https://github.com/stefanprodan/podinfo/issues/474
- https://github.com/stefanprodan/podinfo/pull/480
- https://github.com/stefanprodan/podinfo/commit/cbebb20fd48588d36fc7ff3e874c128eb89692f4
- https://github.com/Niccolo10/Security-Advisories/blob/main/CVE-2026-43644/cve-2026-43644.md
- https://github.com/stefanprodan/podinfo
- https://github.com/stefanprodan/podinfo/releases/tag/6.12.0
- https://www.vulncheck.com/advisories/podinfo-reflected-xss-via-echo-endpoint
