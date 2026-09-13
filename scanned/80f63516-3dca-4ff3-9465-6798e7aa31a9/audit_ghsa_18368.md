# [H] Mattermost Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-qx3f-6vq3-8j8m
CVE: CVE-2025-9079
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-qx3f-6vq3-8j8m
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost-server` — affected >=10.10.0 <10.10.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250707221302-a8fa77f107ef

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17, 10.10.x <= 10.10.1, 10.9.x <= 10.9.3 fail to validate import directory path configuration which allows admin users to execute arbitrary code via malicious plugin upload to prepackaged plugins directory

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9079
- https://github.com/mattermost/mattermost/commit/047a2c64071749367fe02d2162f6103a3d31a883
- https://github.com/mattermost/mattermost/commit/439464883aa16a329c23cd6274c4cca7e88e238f
- https://github.com/mattermost/mattermost/commit/4ff68eea0a3f3777032d31a1a82f4b1fb492a1ac
- https://github.com/mattermost/mattermost/commit/96665b9b98a17534fcd515982a2eb26950581e41
- https://github.com/mattermost/mattermost/commit/a8fa77f107efe83f09a779f8e67cbecf236b0032
- https://github.com/mattermost/mattermost/commit/b38e2eccda182212a8032539658723c7d87e0b7e
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3977
