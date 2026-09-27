# [M] Bazarr Blind Server-Side Request Forgery (SSRF) in the /test/<protocol>/ endpoint

## Summary
Severity: Medium
Advisory: CVE-2023-50266
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-12-15
Source: https://osv.dev/vulnerability/CVE-2023-50266
Type: osv

## Details
Bazarr manages and downloads subtitles. In version 1.2.4, the proxy method in bazarr/bazarr/app/ui.py does not validate the user-controlled protocol and url variables and passes them to requests.get() without any sanitization, which leads to a blind server-side request forgery (SSRF). This issue allows for crafting GET requests to internal and external resources on behalf of the server. 1.3.1 contains a partial fix, which limits the vulnerability to HTTP/HTTPS protocols.

## References
- https://github.com/morpheus65535/bazarr/releases/tag/v1.3.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50266.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50266
- https://securitylab.github.com/advisories/GHSL-2023-192_GHSL-2023-194_bazarr/
- https://github.com/morpheus65535/bazarr/commit/17add7fbb3ae1919a40d505470d499d46df9ae6b
