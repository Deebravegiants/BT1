# [H] Weaviate denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-8697-479h-5mfp
CVE: CVE-2023-38976
CWE: CWE-704
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-22
Source: https://github.com/advisories/GHSA-8697-479h-5mfp
Type: github-advisory

## Affected
- Go: `github.com/weaviate/weaviate` — affected >=1.20.0 <1.20.6
- Go: `github.com/weaviate/weaviate` — affected >=1.19.0 <1.19.13
- Go: `github.com/weaviate/weaviate` — affected >=0 <1.18.6

## Details
### Impact
This vulnerability is a type conversion issue that affects users of Weaviate Server versions 1.20.0 and earlier.
Who is impacted: Users of Weaviate Server versions 1.20.0 and earlier are impacted by this vulnerability.

### Patches
A patch has been developed for this vulnerability.
Patch releases 1.20.6, 1.19.13, and 1.18.6 are fixing this vulnerability in each respective minor version release.
Users are strongly recommended to upgrade to one of these patched versions to address the vulnerability.
Keeping software up-to-date is crucial to avoid security vulnerabilities.

### Workarounds
There are no known workarounds to fix or remediate this vulnerability without upgrading.
Users must upgrade to a patched version to mitigate the risk.

### References 
* https://github.com/weaviate/weaviate/releases/tag/v1.18.6
* https://github.com/weaviate/weaviate/releases/tag/v1.19.13
* https://github.com/weaviate/weaviate/releases/tag/v1.20.6

## References
- https://github.com/weaviate/weaviate/security/advisories/GHSA-8697-479h-5mfp
- https://nvd.nist.gov/vuln/detail/CVE-2023-38976
- https://github.com/weaviate/weaviate/issues/3258
- https://github.com/weaviate/weaviate/pull/3431
- https://github.com/weaviate/weaviate/commit/2a7b208d9aca07e28969e3be82689c184ccf9118
- https://github.com/weaviate/weaviate
- https://github.com/weaviate/weaviate/releases/tag/v1.18.6
- https://github.com/weaviate/weaviate/releases/tag/v1.19.13
- https://github.com/weaviate/weaviate/releases/tag/v1.20.6
