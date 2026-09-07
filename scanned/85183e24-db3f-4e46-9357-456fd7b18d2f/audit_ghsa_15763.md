# [C] CLSA Directory Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9xhh-3m78-gvgj
CVE: CVE-2024-28698
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-9xhh-3m78-gvgj
Type: github-advisory

## Affected
- NuGet: `Csla` — affected >=0 <5.5.4
- NuGet: `Csla` — affected >=6.0.0 <8.0.0
- NuGet: `Csla` — affected >=7.0.0 <8.0.0

## Details
Directory Traversal vulnerability in Marimer LLC CSLA .Net before 8.0 allows a remote attacker to execute arbitrary code via a crafted script to the MobileFormatter component.

Fixes for this issue have been backported to the 5.x, 6.x, and 7.x branches of CSLA. CSLA version 5.5.4 contains a fix. As of time of publication, 6.x and 7.x do not have numbered versions containing the fix but do have fix commits available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28698
- https://github.com/MarimerLLC/csla/pull/3552
- https://github.com/MarimerLLC/csla/commit/2c32a5748a0a4bb0159285dfad61d4050e890080
- https://github.com/MarimerLLC/csla/commit/445bc609bc117f62cabf49e1462f7a43b0f8f9a2
- https://github.com/MarimerLLC/csla/commit/8fbdd8c773bfeb9ba3e52d91b5a664848629b13a
- https://github.com/MarimerLLC/csla/commit/f3a5c3474974f60ce3c8ffbd5d91c23a1e397ea4
- https://github.com/MarimerLLC/csla
- https://github.com/MarimerLLC/csla/releases/tag/v5.5.4
- https://www.intruder.io/research/path-traversal-and-code-execution-in-csla-net-cve-2024-28698
