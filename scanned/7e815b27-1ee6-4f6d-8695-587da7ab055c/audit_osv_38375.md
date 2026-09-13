# [H] OpenObserve has a SSRF Protection Bypass via IPv6 Bracket Notation in validate_enrichment_url

## Summary
Severity: High
Advisory: CVE-2026-39361
Aliases: GHSA-gcwf-3p7h-wm79
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39361
Type: osv

## Details
OpenObserve is a cloud-native observability platform. In 0.70.3 and earlier, the validate_enrichment_url function in src/handler/http/request/enrichment_table/mod.rs fails to block IPv6 addresses because Rust's url crate returns them with surrounding brackets (e.g. "[::1]" not "::1"). An authenticated attacker can reach internal services blocked from external access. On cloud deployments this enables retrieval of IAM credentials via AWS IMDSv1 (169.254.169.254), GCP metadata, or Azure IMDS. On self-hosted deployments it allows probing internal network services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39361.json
- https://github.com/openobserve/openobserve/security/advisories/GHSA-gcwf-3p7h-wm79
- https://nvd.nist.gov/vuln/detail/CVE-2026-39361
- https://github.com/openobserve/openobserve/commit/d1a5d8f65b432e2e82f83231390dec7f107e8d75
