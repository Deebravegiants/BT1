# [C] Eigent Allows Arbitrary Code Execution via pull_request_target CI Workflow

## Summary
Severity: Critical
Advisory: CVE-2026-22869
Aliases: GHSA-gvh4-93cq-5xxp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2026-22869
Type: osv

## Details
Eigent is a multi-agent Workforce. A critical security vulnerability in the CI workflow (.github/workflows/ci.yml) allows arbitrary code execution from fork pull requests with repository write permissions. The vulnerable workflow uses pull_request_target trigger combined with checkout of untrusted PR code. An attacker can exploit this to steal credentials, post comments, push code, or create releases.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22869.json
- https://github.com/eigent-ai/eigent/security/advisories/GHSA-gvh4-93cq-5xxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-22869
- https://github.com/eigent-ai/eigent/commit/bf02500bbbab0f01cd0ed8e6dc21fe5683d6bfb5
- https://github.com/eigent-ai/eigent/pull/836
- https://github.com/eigent-ai/eigent/pull/837
