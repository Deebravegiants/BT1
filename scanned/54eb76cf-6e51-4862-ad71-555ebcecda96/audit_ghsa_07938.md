# [M] @langchain/community affected by SSRF Bypass in RecursiveUrlLoader via insufficient URL origin validation

## Summary
Severity: Medium
Advisory: GHSA-gf3v-fwqg-4vh7
CVE: CVE-2026-26019
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-gf3v-fwqg-4vh7
Type: github-advisory

## Affected
- npm: `@langchain/community` — affected >=0 <1.1.14

## Details
## Description

The `RecursiveUrlLoader` class in `@langchain/community` is a web crawler that recursively follows links from a starting URL. Its `preventOutside` option (enabled by default) is intended to restrict crawling to the same site as the base URL.

The implementation used `String.startsWith()` to compare URLs, which does not perform semantic URL validation. An attacker who controls content on a crawled page could include links to domains that share a string prefix with the target (e.g., `https://example.com.attacker.com` passes a `startsWith` check against `https://example.com`), causing the crawler to follow links to attacker-controlled or internal infrastructure.

Additionally, the crawler performed no validation against private or reserved IP addresses. A crawled page could include links targeting cloud metadata services (`169.254.169.254`), localhost, or RFC 1918 addresses, and the crawler would fetch them without restriction.

## Impact

An attacker who can influence the content of a page being crawled (e.g., by placing a link on a public-facing page, forum, or user-generated content) could cause the crawler to:

- Fetch cloud instance metadata (AWS, GCP, Azure), potentially exposing IAM credentials and session tokens
- Access internal services on private networks (`10.x`, `172.16.x`, `192.168.x`)
- Connect to localhost services
- Exfiltrate response data via attacker-controlled redirect chains

This is exploitable in any environment where `RecursiveUrlLoader` runs on infrastructure with access to cloud metadata or internal services — which includes most cloud-hosted deployments.

## Resolution

Two changes were made:

1. **Origin comparison replaced.** The `startsWith` check was replaced with a strict origin comparison using the URL API (`new URL(link).origin === new URL(baseUrl).origin`). This correctly validates scheme, hostname, and port as a unit, preventing subdomain-based bypasses.

2. **SSRF validation added to all fetch operations.** A new URL validation module (`@langchain/core/utils/ssrf`) was introduced and applied before every outbound fetch in the crawler. This blocks requests to:
   - **Cloud metadata endpoints:** `169.254.169.254`, `169.254.170.2`, `100.100.100.200`, `metadata.google.internal`, and related hostnames
   - **Private IP ranges:** `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`
   - **IPv6 equivalents:** `::1`, `fc00::/7`, `fe80::/10`
   - **Non-HTTP/HTTPS schemes** (`file:`, `ftp:`, `javascript:`, etc.)

Cloud metadata endpoints are unconditionally blocked and cannot be overridden.

## Workarounds

Users who cannot upgrade immediately should avoid using `RecursiveUrlLoader` on untrusted or user-influenced content, or should run the crawler in a network environment without access to cloud metadata or internal services.

## References
- https://github.com/langchain-ai/langchainjs/security/advisories/GHSA-gf3v-fwqg-4vh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-26019
- https://github.com/langchain-ai/langchainjs/pull/9990
- https://github.com/langchain-ai/langchainjs/commit/d5e3db0d01ab321ec70a875805b2f74aefdadf9d
- https://github.com/langchain-ai/langchainjs
- https://github.com/langchain-ai/langchainjs/releases/tag/%40langchain%2Fcommunity%401.1.14
