# [H] Plexus-Utils has a Directory Traversal vulnerability in its extractFile method 

## Summary
Severity: High
Advisory: GHSA-6fmv-xxpf-w3cw
CVE: CVE-2025-67030
CWE: CWE-22
Ecosystem: Maven
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-6fmv-xxpf-w3cw
Type: github-advisory

## Affected
- Maven: `org.codehaus.plexus:plexus-utils` — affected >=4.0.0 <4.0.3
- Maven: `org.codehaus.plexus:plexus-utils` — affected >=0 <3.6.1

## Details
Directory Traversal vulnerability in the extractFile method of org.codehaus.plexus.util.Expand in plexus-utils before 6d780b3378829318ba5c2d29547e0012d5b29642. This allows an attacker to execute arbitrary code

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67030
- https://github.com/codehaus-plexus/plexus-utils/issues/294
- https://github.com/codehaus-plexus/plexus-utils/pull/295
- https://github.com/codehaus-plexus/plexus-utils/pull/296
- https://github.com/codehaus-plexus/plexus-utils/commit/6d780b3378829318ba5c2d29547e0012d5b29642
- https://gist.github.com/weaver4VD/3216dac645220f8c9b488362f61241ec
- https://github.com/codehaus-plexus/plexus-utils
- https://github.com/codehaus-plexus/plexus-utils/releases/tag/plexus-utils-4.0.3
