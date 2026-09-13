# [C] MailDev Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-vc6q-ccj9-9r89
CVE: CVE-2024-27448
CWE: CWE-22, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-vc6q-ccj9-9r89
Type: github-advisory

## Affected
- npm: `maildev` — affected >=2.0.0-beta1

## Details
MailDev 2 through 2.1.0 allows Remote Code Execution via a crafted Content-ID header for an e-mail attachment, leading to `lib/mailserver.js` writing arbitrary code into the `routes.js` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27448
- https://github.com/maildev/maildev/issues/467
- https://gist.github.com/stypr/fe2003f00959f7e3d92ab9d5260433f8
- https://github.com/Tim-Hoekstra/MailDev-2.1.0-Exploit-RCE
- https://github.com/maildev/maildev
- https://github.com/maildev/maildev/releases
- https://intrix.com.au/articles/exposing-major-security-flaw-in-maildev
