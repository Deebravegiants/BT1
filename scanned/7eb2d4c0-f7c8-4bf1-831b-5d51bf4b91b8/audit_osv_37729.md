# [H] AVideo-Encoder has Unauthenticated Blind Server-Side Request Forgery via Public Thumbnail Generator

## Summary
Severity: High
Advisory: CVE-2026-33024
Aliases: GHSA-h9gh-866r-6vgq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33024
Type: osv

## Details
AVideo is a video-sharing Platform. Versions prior to 8.0 contain a Server-Side Request Forgery vulnerability (CWE-918) in the public thumbnail endpoints getImage.php and getImageMP4.php. Both endpoints accept a base64Url GET parameter, base64-decode it, and pass the resulting URL to ffmpeg as an input source without any authentication requirement. The prior validation only checked that the URL was syntactically valid (FILTER_VALIDATE_URL) and started with http(s)://. This is insufficient: an attacker can supply URLs such as http://169.254.169.254/latest/meta-data/ (AWS/cloud instance metadata), http://192.168.x.x/, or http://127.0.0.1/ to make the server reach internal network resources. The response is not directly returned (blind), but timing differences and error logs can be used to infer results. The issue has been fixed in version 8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33024.json
- https://github.com/WWBN/AVideo-Encoder/security/advisories/GHSA-h9gh-866r-6vgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33024
- https://github.com/WWBN/AVideo-Encoder/commit/f9df098534a0e05fd431e771ac9d70f0f36f1c06
