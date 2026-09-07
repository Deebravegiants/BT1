# [M] Wagtail vulnerable to denial-of-service via memory exhaustion when uploading large files

## Summary
Severity: Medium
Advisory: GHSA-33pv-vcgh-jfg9
CVE: CVE-2023-28837
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-04-03
Source: https://github.com/advisories/GHSA-33pv-vcgh-jfg9
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=4.2 <4.2.2
- PyPI: `wagtail` — affected >=0 <4.1.4

## Details
### Impact

A memory exhaustion bug exists in Wagtail's handling of uploaded images and documents. For both images and documents, files are loaded into memory during upload for additional processing. A user with access to upload images or documents through the Wagtail admin interface could upload a file so large that it results in a crash or denial of service.

The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin. It can only be exploited by admin users with permission to upload images or documents.

Image uploads are [restricted to 10MB by default](https://docs.wagtail.org/en/stable/reference/settings.html#wagtailimages-max-upload-size), however this validation only happens on the frontend and on the backend after the vulnerable code. 

### Patches

Patched versions have been released as Wagtail 4.1.4 (for the LTS 4.1 branch) and Wagtail 4.2.2 (for the current 4.2 branch).

### Workarounds

Site owners who are unable to upgrade to the new versions are encouraged to add extra protections outside of Wagtail to limit the size of uploaded files. Exactly how this is done will vary based on your hosting environment, but here are a few references for common setups:

- Nginx: [`client_max_body_size`](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)
- Apache: [`LimitRequestBody`](https://httpd.apache.org/docs/2.4/mod/core.html#limitrequestbody)
- Cloudflare: Already [imposes a limit of 100MB - 500MB](https://developers.cloudflare.com/cache/about/default-cache-behavior#customization-options-and-limitations) depending on plan
- CloudFront: [`SizeConstraint`](https://docs.aws.amazon.com/waf/latest/APIReference/API_SizeConstraintStatement.html)
- Traefik: [`traefik.http.middlewares.limit.buffering.maxRequestBodyBytes`](https://doc.traefik.io/traefik/middlewares/http/buffering/#maxrequestbodybytes)

The changes themselves are deep inside Wagtail, making patching incredibly difficult.

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-33pv-vcgh-jfg9
- https://nvd.nist.gov/vuln/detail/CVE-2023-28837
- https://github.com/wagtail/wagtail/commit/3c0c64642b9e5b8d28b111263c7f4bddad6c3880
- https://github.com/wagtail/wagtail/commit/c9d2fcd650a88d76ae122646142245e5927a9165
- https://github.com/wagtail/wagtail/commit/cfa11bbe00dbe7ce8cd4c0bbfe2a898a690df2bf
- https://github.com/wagtail/wagtail/commit/d4022310cbe497993459c3136311467c7ac6329a
- https://docs.wagtail.org/en/stable/reference/settings.html#wagtailimages-max-upload-size
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2023-56.yaml
- https://github.com/wagtail/wagtail
- https://github.com/wagtail/wagtail/releases/tag/v4.1.4
- https://github.com/wagtail/wagtail/releases/tag/v4.2.2
