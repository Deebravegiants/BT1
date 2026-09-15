# [H] SRS has command injection vulnerability in demonstration api-server for HTTP callback.

## Summary
Severity: High
Advisory: CVE-2023-34105
Aliases: GHSA-vpr5-779c-cx62
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-12
Source: https://osv.dev/vulnerability/CVE-2023-34105
Type: osv

## Details
SRS is a real-time video server supporting RTMP, WebRTC, HLS, HTTP-FLV, SRT, MPEG-DASH, and GB28181. Prior to versions 5.0.157, 5.0-b1, and 6.0.48, SRS's `api-server` server is vulnerable to a drive-by command injection. An attacker may send a request to the `/api/v1/snapshots` endpoint containing any commands to be executed as part of the body of the POST request. This issue may lead to Remote Code Execution (RCE). Versions 5.0.157, 5.0-b1, and 6.0.48 contain a fix.

## References
- https://github.com/ossrs/srs/blob/1d11d02e4b82fc3f37e4b048cff483b1581482c1/trunk/research/api-server/server.go#L761
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34105.json
- https://github.com/ossrs/srs/security/advisories/GHSA-vpr5-779c-cx62
- https://nvd.nist.gov/vuln/detail/CVE-2023-34105
- https://github.com/ossrs/srs/commit/1d878c2daaf913ad01c6d0bc2f247116c8050338
