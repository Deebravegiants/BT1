# [M] OZI-Project/ozi-publish Code Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2487-9f55-2vg9
CVE: CVE-2025-47271
CWE: CWE-1116, CWE-94, CWE-95
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-05-12
Source: https://github.com/advisories/GHSA-2487-9f55-2vg9
Type: github-advisory

## Affected
- GitHub Actions: `OZI-Project/publish` — affected >=1.13.2 <1.13.6

## Details
### Impact
Potentially untrusted data flows into PR creation logic. A malicious actor could construct a branch name that injects arbitrary code.

### Patches
This is patched in 1.13.6

### Workarounds
Downgrade to <1.13.2

### References

* [Understanding the Risk of Script Injections](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#understanding-the-risk-of-script-injections)

## References
- https://github.com/OZI-Project/publish/security/advisories/GHSA-2487-9f55-2vg9
- https://nvd.nist.gov/vuln/detail/CVE-2025-47271
- https://github.com/OZI-Project/publish/commit/abd8524ec69800890529846b3ccfb09ce7c10b5c
- https://github.com/OZI-Project/publish
