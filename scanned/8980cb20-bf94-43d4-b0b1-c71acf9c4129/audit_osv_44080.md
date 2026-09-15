# [M] NLTK before 3.10.3 SSRF Protection Bypass via Proxy

## Summary
Severity: Medium
Advisory: CVE-2026-78682
Aliases: GHSA-6ww7-3frv-cqxh, PYSEC-2026-3733
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78682
Type: osv

## Details
NLTK before 3.10.3 contains a server-side request forgery vulnerability in nltk.pathsec.urlopen (and callers nltk.data.load, nltk.downloader.Downloader.index/download) when an HTTP proxy is configured. pathsec.urlopen validates the requested hostname locally, but proxy-handler inheritance disables the safe HTTP/HTTPS handlers so the actual fetch is performed by the proxy against a destination that is never re-validated. An attacker can supply a validated public URL that the proxy forwards to an internal loopback-only service, allowing disclosure of internal HTTP resources, loading of forged downloader indexes, and installation of attacker-chosen package content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78682.json
- https://github.com/nltk/nltk/security/advisories/GHSA-6ww7-3frv-cqxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-78682
- https://www.vulncheck.com/advisories/nltk-before-ssrf-protection-bypass-via-proxy
