# [H] Shields.io Remote Code Execution vulnerability in Dynamic JSON/TOML/YAML badges

## Summary
Severity: High
Advisory: CVE-2024-47180
Aliases: GHSA-rxvx-x284-4445
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-47180
Type: osv

## Details
Shields.io is a service for concise, consistent, and legible badges in SVG and raster format. Shields.io and users self-hosting their own instance of shields using version < `server-2024-09-25` are vulnerable to a remote execution vulnerability via the JSONPath library used by the Dynamic JSON/Toml/Yaml badges. This vulnerability would allow any user with access to make a request to a URL on the instance to the ability to execute code by crafting a malicious JSONPath expression. All users who self-host an instance are vulnerable. This problem was fixed in server-2024-09-25. Those who follow the tagged releases should update to `server-2024-09-25` or later. Those who follow the rolling tag on DockerHub, `docker pull shieldsio/shields:next` to update to the latest version. As a workaround, blocking access to the endpoints `/badge/dynamic/json`, `/badge/dynamic/toml`, and `/badge/dynamic/yaml` (e.g: via a firewall or reverse proxy in front of your instance) would prevent the exploitable endpoints from being accessed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47180.json
- https://github.com/badges/shields/security/advisories/GHSA-rxvx-x284-4445
- https://nvd.nist.gov/vuln/detail/CVE-2024-47180
- https://github.com/badges/shields/issues/10553
- https://github.com/badges/shields/commit/ec1b6c8daccda075403c1688ac02603f7aaa50b2
- https://github.com/badges/shields/pull/10551
