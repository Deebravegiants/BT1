# [H] CVE-2019-11937

## Summary
Severity: High
Advisory: CVE-2019-11937
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-04
Source: https://osv.dev/vulnerability/CVE-2019-11937
Type: osv

## Details
In Mcrouter prior to v0.41.0, a large struct input provided to the Carbon protocol reader could result in stack exhaustion and denial of service.

## References
- https://github.com/facebook/mcrouter/releases/tag/v0.41.0-release
- https://www.facebook.com/security/advisories/cve-2019-11937
- https://github.com/facebook/mcrouter/commit/97e033b3bb0cb16b61bf49f0dc7f311a3e0edd1b
