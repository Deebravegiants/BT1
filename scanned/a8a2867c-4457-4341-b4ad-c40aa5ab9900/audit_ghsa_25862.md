# [C] Server-Side Request Forgery in calibreweb

## Summary
Severity: Critical
Advisory: GHSA-2647-c639-qv2j
CVE: CVE-2022-0766
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-08
Source: https://github.com/advisories/GHSA-2647-c639-qv2j
Type: github-advisory

## Affected
- PyPI: `calibreweb` — affected >=0 <0.6.17

## Details
calibreweb prior to version 0.6.17 is vulnerable to server-side request forgery (SSRF). This is due to an incomplete fix for [CVE-2022-0339](https://github.com/advisories/GHSA-4w8p-x6g8-fv64). The blacklist does not check for `0.0.0.0`, which would result in a payload of `0.0.0.0` resolving to `localhost`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0766
- https://github.com/janeczku/calibre-web/commit/965352c8d96c9eae7a6867ff76b0db137d04b0b8
- https://github.com/janeczku/calibre-web
- https://huntr.dev/bounties/7f2a5bb4-e6c7-4b6a-b8eb-face9e3add7b
