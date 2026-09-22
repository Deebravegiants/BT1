# [M] OpenClaw < 2026.6.1 Denial of Service via Remote Media URLs

## Summary
Severity: Medium
Advisory: CVE-2026-62210
Aliases: GHSA-4xwj-mcc7-x7x5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62210
Type: osv

## Details
OpenClaw versions before 2026.6.1 contain a denial of service vulnerability where remote media URLs can trigger slow-read attacks that exhaust gateway worker resources. Attackers with access to configured input paths can supply remote media URLs that consume gateway resources and reduce availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62210.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4xwj-mcc7-x7x5
- https://nvd.nist.gov/vuln/detail/CVE-2026-62210
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-remote-media-urls
- https://github.com/openclaw/openclaw
