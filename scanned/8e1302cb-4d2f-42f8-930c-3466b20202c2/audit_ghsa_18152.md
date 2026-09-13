# [M] Fides Webserver API Rate Limiting Vulnerability in Proxied Environments

## Summary
Severity: Medium
Advisory: GHSA-fq34-xw6c-fphf
CVE: CVE-2025-57816
CWE: CWE-307, CWE-770, CWE-799
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-fq34-xw6c-fphf
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=0 <2.69.1

## Details
### Summary

The Fides Webserver API's built-in IP-based rate limiting is ineffective in environments with CDNs, proxies or load balancers. The system incorrectly applies rate limits based on directly connected infrastructure IPs rather than client IPs, and stores counters in-memory rather than in a shared store. This allows attackers to bypass intended rate limits and potentially cause denial of service.

This vulnerability only affects deployments relying on Fides's built-in rate limiting for protection. Deployments using external rate limiting solutions (WAFs, API gateways, etc.) are not affected.

### Details

The vulnerability has two components:

1. Rate limiting uses the immediate connection source IP instead of the actual client IP
2. Rate limit counters are maintained in-memory per container rather than in a shared store

In production environments, these issues allow clients to exceed intended rate limits and enable attackers to trigger rate limits on infrastructure IPs, causing legitimate clients to receive 429 responses.

### Impact

This vulnerability affects availability, allowing attackers to:

- Bypass rate limits, potentially leading to resource exhaustion
- Cause a denial of service for legitimate clients by deliberately triggering rate limits on infrastructure IPs

### Patches

The vulnerability has been patched in Fides version `2.69.1`. Users are advised to upgrade to this version or later to secure their systems against this threat.

### Workarounds

There are no application-level workarounds. However, rate limiting may instead be implemented externally at the infrastructure level using a WAF, API Gateway, or similar technology.

### Risk Level

This vulnerability has been assigned a severity of MEDIUM.

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-fq34-xw6c-fphf
- https://nvd.nist.gov/vuln/detail/CVE-2025-57816
- https://github.com/ethyca/fides/commit/59903c195e2f9f8915a1db94950aefd557033a5c
- https://github.com/ethyca/fides
- https://github.com/ethyca/fides/releases/tag/2.69.1
