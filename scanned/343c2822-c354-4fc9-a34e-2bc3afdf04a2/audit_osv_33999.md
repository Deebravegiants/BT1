# [H] LibHTP's memory leak with lzma can lead to resource starvation

## Summary
Severity: High
Advisory: CVE-2025-53537
Aliases: GHSA-v3qq-h8mh-vph7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-23
Source: https://osv.dev/vulnerability/CVE-2025-53537
Type: osv

## Details
LibHTP is a security-aware parser for the HTTP protocol and its related bits and pieces. In versions 0.5.50 and below, there is a traffic-induced memory leak that can starve the process of memory, leading to loss of visibility. To workaround this issue, set `suricata.yaml app-layer.protocols.http.libhtp.default-config.lzma-enabled` to false. This issue is fixed in version 0.5.51.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53537.json
- https://github.com/OISF/libhtp/security/advisories/GHSA-v3qq-h8mh-vph7
- https://nvd.nist.gov/vuln/detail/CVE-2025-53537
- https://github.com/OISF/libhtp/commit/9037ea35110a0d97be5cedf8d31fb4cd9a38c7a7
