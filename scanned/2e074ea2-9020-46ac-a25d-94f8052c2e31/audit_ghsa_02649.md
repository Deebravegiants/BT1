# [H] Elvish vulnerable to remote code execution via the web UI backend

## Summary
Severity: High
Advisory: GHSA-fpv6-f8jw-rc3r
CVE: CVE-2021-41088
CWE: CWE-346, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-23
Source: https://github.com/advisories/GHSA-fpv6-f8jw-rc3r
Type: github-advisory

## Affected
- Go: `github.com/elves/elvish` — affected >=0 <0.14.0

## Details
### Impact

Elvish's backend for the experimental web UI (started by `elvish -web`) hosts an endpoint that allows executing the code sent from the web UI.

The backend does not check the origin of requests correctly. As a result, if the user has the web UI backend open and visits a compromised or malicious website, the website can send arbitrary code to the endpoint in localhost.

### Patches

All Elvish releases since 0.14.0 no longer include the experimental web UI, although it is still possible for the user to build a version from source that includes it.

The issue can be patched for previous versions by removing the web UI (found in web, pkg/web or pkg/prog/web, depending on the exact version).

### Workarounds

Do not use the experimental web UI.

### For more information

If you have any questions or comments about this advisory, please email xiaqqaix@gmail.com.

## References
- https://github.com/elves/elvish/security/advisories/GHSA-fpv6-f8jw-rc3r
- https://nvd.nist.gov/vuln/detail/CVE-2021-41088
- https://github.com/elves/elvish/commit/ccc2750037bbbfafe9c1b7a78eadd3bd16e81fe5
- https://github.com/elves/elvish
