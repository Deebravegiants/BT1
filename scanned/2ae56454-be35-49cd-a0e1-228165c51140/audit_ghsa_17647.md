# [C] @nx/azure-cache Vulnerable to Build Cache Poisoning via Untrusted Pull Requests

## Summary
Severity: Critical
Advisory: GHSA-rrr2-jcr8-7q3x
CVE: CVE-2025-36852
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:P/AU:Y/R:U/V:C/RE:M/U:Red (CVSS_V4)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-rrr2-jcr8-7q3x
Type: github-advisory

## Affected
- npm: `@nx/azure-cache` — affected >=0

## Details
A critical security vulnerability exists in remote cache extensions for common build systems utilizing bucket-based remote cache (such as those using Amazon S3, Google Cloud Storage, or similar object storage) that allows any contributor with pull request privileges to inject compromised artifacts from an untrusted environment into trusted production environments without detection. 

The vulnerability exploits a fundamental design flaw in the "first-to-cache wins" principle, where artifacts built in untrusted environments (feature branches, pull requests) can poison the cache used by trusted environments (protected branches, production deployments). 

This attack bypasses all traditional security measures including encryption, access controls, and checksum validation because the poisoning occurs during the artifact construction phase, before any security measures are applied.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-36852
- https://github.com/nrwl/nx
- https://nx.app/files/cve-2025-06
- https://nx.dev/blog/creep-vulnerability-build-cache-security
- https://nx.dev/docs/reference/remote-cache-plugins/azure-cache/overview
