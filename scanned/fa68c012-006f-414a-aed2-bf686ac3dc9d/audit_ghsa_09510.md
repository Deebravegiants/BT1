# [M] Volcano's webhook server vulnerable to OOM due to unbounded HTTP request body size

## Summary
Severity: Medium
Advisory: GHSA-8wxp-xxp2-rcgx
CVE: CVE-2026-44247
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-8wxp-xxp2-rcgx
Type: github-advisory

## Affected
- Go: `volcano.sh/volcano` — affected >=0 <1.12.4
- Go: `volcano.sh/volcano` — affected >=1.13.0 <1.13.3
- Go: `volcano.sh/volcano` — affected >=1.14.0 <1.14.2

## Details
### Impact
The Volcano webhook server does not enforce a size limit on incoming HTTP request bodies. Any in-cluster pod that can reach the webhook endpoint may send an arbitrarily large request body, potentially causing the webhook server to be killed by OOM. All Volcano deployments with the webhook server exposed to in-cluster traffic are affected.

### Patches
This issue will be fixed in the following versions:
- v1.14.2
- v1.13.3
- v1.12.4

Users running versions below these should upgrade accordingly.

### Workarounds
No known workarounds. Upgrade to the patched versions listed above.

## References
- https://github.com/volcano-sh/volcano/security/advisories/GHSA-8wxp-xxp2-rcgx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44247
- https://github.com/volcano-sh/volcano
