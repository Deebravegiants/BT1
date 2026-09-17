# [M] PILOS: Reverse tabnabbing in room description

## Summary
Severity: Medium
Advisory: CVE-2026-71555
Aliases: GHSA-j4wr-p8gh-xrw5
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-71555
Type: osv

## Details
PILOS (Platform for Interactive Live-Online Seminars) is a frontend for BigBlueButton. From 2.1.0 until 4.14.1, PILOS does not send a Cross-Origin-Opener-Policy response header, so pages opened by PILOS via a link that opens a new browsing context (e.g., target="_blank") retain a window.opener reference back to the originating PILOS tab. A malicious destination page reached this way can use window.opener to navigate or manipulate the original PILOS tab, a technique known as reverse tabnabbing, potentially redirecting an authenticated user to a phishing page that mimics PILOS. This issue is fixed in version 4.14.1.

## References
- https://github.com/THM-Health/PILOS/releases/tag/v4.14.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71555.json
- https://github.com/THM-Health/PILOS/security/advisories/GHSA-j4wr-p8gh-xrw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-71555
- https://github.com/THM-Health/PILOS/commit/b50f2bd07c4f4a7d6a9981578238ae3579275d81
