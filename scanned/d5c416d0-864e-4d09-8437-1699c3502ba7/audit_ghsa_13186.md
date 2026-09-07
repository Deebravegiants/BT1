# [C] sing-box vulnerable to improper authentication in the SOCKS inbound

## Summary
Severity: Critical
Advisory: GHSA-r5hm-mp3j-285g
CVE: CVE-2023-43644
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2023-09-26
Source: https://github.com/advisories/GHSA-r5hm-mp3j-285g
Type: github-advisory

## Affected
- Go: `github.com/sagernet/sing-box` — affected >=0 <1.4.5
- Go: `github.com/sagernet/sing-box` — affected >=1.5.0-beta.1 <1.5.0-rc.5
- Go: `github.com/sagernet/sing` — affected >=0 <0.2.12-0.20230925092853-5b05b5c147d9

## Details
### Impact

This vulnerability allows specially crafted requests to bypass authentication, affecting all SOCKS inbounds with user authentication.

### Patches

Update to sing-box 1.4.5 or 1.5.0-rc.5 and later versions.

### Workarounds

Don't expose the SOCKS5 inbound to insecure environments.

## References
- https://github.com/SagerNet/sing-box/security/advisories/GHSA-r5hm-mp3j-285g
- https://nvd.nist.gov/vuln/detail/CVE-2023-43644
- https://github.com/SagerNet/sing-box/commit/9891fd672f5da9f20f59a1693271a946727f49e2
- https://github.com/SagerNet/sing/commit/5b05b5c147d9650e8accb4441e216c72a61f4859
- https://github.com/SagerNet/sing-box
- https://github.com/SagerNet/sing-box/releases/tag/v1.4.5
