# [H] Arbitrary file read vulnerability in Shoko Server

## Summary
Severity: High
Advisory: CVE-2023-43662
Aliases: GHSA-mwcv-ghjq-8f2g
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-09-28
Source: https://osv.dev/vulnerability/CVE-2023-43662
Type: osv

## Details
ShokoServer is a media server which specializes in organizing anime. In affected versions the `/api/Image/WithPath` endpoint is accessible without authentication and is supposed to return default server images. The endpoint accepts the parameter `serverImagePath`, which is not sanitized in any way before being passed to `System.IO.File.OpenRead`, which results in an arbitrary file read. This issue may lead to an arbitrary file read which is exacerbated in the windows installer which installs the ShokoServer as administrator. Any unauthenticated attacker may be able to access sensitive information and read files stored on the server. The `/api/Image/WithPath` endpoint has been removed in commit `6c57ba0f0` which will be included in subsequent releases. Users should limit access to the `/api/Image/WithPath` endpoint or manually patch their installations until a patched release is made. This issue was discovered by the GitHub Security lab and is also indexed as GHSL-2023-191.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43662.json
- https://github.com/ShokoAnime/ShokoServer/security/advisories/GHSA-mwcv-ghjq-8f2g
- https://nvd.nist.gov/vuln/detail/CVE-2023-43662
- https://github.com/ShokoAnime/ShokoServer/commit/6c57ba0f073d6be5a4f508c46c2ce36727cbce80
