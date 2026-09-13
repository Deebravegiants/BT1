# [H] CVE-2025-44137

## Summary
Severity: High
Advisory: CVE-2025-44137
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2025-07-29
Source: https://osv.dev/vulnerability/CVE-2025-44137
Type: osv

## Details
MapTiler Tileserver-php v2.0 is vulnerable to Directory Traversal. The renderTile function within tileserver.php is responsible for delivering tiles that are stored as files on the server via web request. Creating the path to a file allows the insertion of "../" and thus read any file on the web server. Affected GET parameters are "TileMatrix", "TileRow", "TileCol" and "Format"

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/44xxx/CVE-2025-44137.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-44137
- https://github.com/maptiler/tileserver-php/issues/167
- https://github.com/maptiler/tileserver-php/commit/4fe14e6164bbe2a3f9e3b3d7acf303e3ec210c8e
- https://github.com/mheranco/CVE-2025-44137
