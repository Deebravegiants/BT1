# [C] Server-Side Request Forgery (SSRF) in rudloff/alltube

## Summary
Severity: Critical
Advisory: GHSA-r5hc-wm3g-hjw6
CVE: CVE-2022-0768
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-01
Source: https://github.com/advisories/GHSA-r5hc-wm3g-hjw6
Type: github-advisory

## Affected
- Packagist: `rudloff/alltube` — affected >=0 <3.0.2

## Details
### Impact
Releases prior to 3.0.2 are vulnerable to a Server-Side Request Forgery vulnerability that allows an attacker to send a request to an internal hostname.

### Patches
3.0.2 contains a fix for this vulnerability.
(The 1.x and 2.x releases are not maintained anymore.)

Part of the fix requires applying [a patch](https://github.com/Rudloff/alltube/blob/148a171b240e7ceb076b9e198bef412de14ac55d/patches/youtube-dl-redirect.diff) to youtube-dl to prevent it from following HTTP redirects. If you are using the version of youtube-dl bundled with 3.0.2, it is already patched.
However, if you are using your own unpatched version of youtube-dl **you might still be vulnerable**.

### References
* https://github.com/Rudloff/alltube/commit/3a4f09dda0a466662a4e52cde674749e0c668e8d
* https://github.com/Rudloff/alltube/commit/1b099bb9836a3ce7c427a41722a7ab5a3d1c1b2d
* https://huntr.dev/bounties/9b14cc46-ec08-4940-83cc-9f986b2a5903/
* https://nvd.nist.gov/vuln/detail/CVE-2022-0768
* https://github.com/ytdl-org/youtube-dl/issues/30691

## References
- https://github.com/Rudloff/alltube/security/advisories/GHSA-r5hc-wm3g-hjw6
- https://nvd.nist.gov/vuln/detail/CVE-2022-0768
- https://github.com/Rudloff/alltube/commit/3a4f09dda0a466662a4e52cde674749e0c668e8d
- https://github.com/rudloff/alltube/commit/148a171b240e7ceb076b9e198bef412de14ac55d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/rudloff/alltube/CVE-2022-0768.yaml
- https://github.com/Rudloff/alltube
- https://huntr.dev/bounties/9b14cc46-ec08-4940-83cc-9f986b2a5903
