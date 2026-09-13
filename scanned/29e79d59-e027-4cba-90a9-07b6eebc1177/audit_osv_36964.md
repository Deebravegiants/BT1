# [H] Wallos: SSRF via Redirect Bypass in Logo/Icon URL Fetch

## Summary
Severity: High
Advisory: CVE-2026-27479
Aliases: GHSA-fgmf-7g5v-jmjg
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27479
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Versions 4.6.0 and below contain a Server-Side Request Forgery (SSRF) vulnerability in the subscription and payment logo/icon upload functionality. The application validates the IP address of the provided URL before making the request, but allows HTTP redirects (CURLOPT_FOLLOWLOCATION = true), enabling an attacker to bypass the IP validation and access internal resources, including cloud instance metadata endpoints. The getLogoFromUrl() function validates the URL by resolving the hostname and checking if the resulting IP is in a private or reserved range using FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE. However, the subsequent cURL request is configured with CURLOPT_FOLLOWLOCATION = true and CURLOPT_MAXREDIRS = 3, which means the request will follow HTTP redirects without re-validating the destination IP. This issue has been fixed in version 4.6.1.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27479.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-fgmf-7g5v-jmjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-27479
- https://github.com/ellite/Wallos/commit/76a53df9cb4658123b8f0b7cf1826f1ba7d1c960
