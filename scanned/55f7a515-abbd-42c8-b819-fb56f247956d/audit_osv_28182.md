# [H] Excessive CPU used on malformed traffic

## Summary
Severity: High
Advisory: CVE-2024-28871
Aliases: GHSA-ffr2-45w9-7wmg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-28871
Type: osv

## Details
LibHTP is a security-aware parser for the HTTP protocol and the related bits and pieces. Version 0.5.46 may parse malformed request traffic, leading to excessive CPU usage. Version 0.5.47 contains a patch for the issue. No known workarounds are available.

## References
- https://redmine.openinfosecfoundation.org/issues/6757
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28871.json
- https://github.com/OISF/libhtp/security/advisories/GHSA-ffr2-45w9-7wmg
- https://nvd.nist.gov/vuln/detail/CVE-2024-28871
- https://github.com/OISF/libhtp/commit/79e713f3e527593a45f545e854cd9e6fbb3cd3ed
- https://github.com/OISF/libhtp/commit/bf618ec7f243cebfb0f7e84c3cb158955cb32b4d
