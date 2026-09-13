# [H] Allocation of Resources Without Limits or Throttling in flagd

## Summary
Severity: High
Advisory: CVE-2026-31866
Aliases: GHSA-rmrf-g9r3-73pm, GO-2026-4674
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31866
Type: osv

## Details
flagd is a feature flag daemon with a Unix philosophy. Prior to 0.14.2, flagd exposes OFREP (/ofrep/v1/evaluate/...) and gRPC (evaluation.v1, evaluation.v2) endpoints for feature flag evaluation. These endpoints are designed to be publicly accessible by client applications. The evaluation context included in request payloads is read into memory without any size restriction. An attacker can send a single HTTP request with an arbitrarily large body, causing flagd to allocate a corresponding amount of memory. This leads to immediate memory exhaustion and process termination (e.g., OOMKill in Kubernetes environments). flagd does not natively enforce authentication on its evaluation endpoints. While operators may deploy flagd behind an authenticating reverse proxy or similar infrastructure, the endpoints themselves impose no access control by default. This vulnerability is fixed in 0.14.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31866.json
- https://github.com/open-feature/flagd/security/advisories/GHSA-rmrf-g9r3-73pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-31866
- https://github.com/open-feature/flagd/commit/25c5fd7e80c26eb2c00b20317b2456fe6f927ea3
