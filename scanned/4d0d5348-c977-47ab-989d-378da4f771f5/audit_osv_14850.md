# [H] CVE-2019-11923

## Summary
Severity: High
Advisory: CVE-2019-11923
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-11923
Type: osv

## Details
In Mcrouter prior to v0.41.0, the deprecated ASCII parser would allocate a buffer to a user-specified length with no maximum length enforced, allowing for resource exhaustion or denial of service.

## References
- https://github.com/facebook/mcrouter/releases/tag/v0.41.0-release
- https://www.facebook.com/security/advisories/cve-2019-11923
- https://github.com/facebook/mcrouter/commit/98ce6624cd2563cfdb5da3b2949d5e1e03867034
