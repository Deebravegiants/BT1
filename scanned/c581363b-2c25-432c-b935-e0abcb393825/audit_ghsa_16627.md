# [M] Scrapy allows redirect following in protocols other than HTTP

## Summary
Severity: Medium
Advisory: GHSA-23j4-mw76-5v7h
CWE: CWE-552
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-23j4-mw76-5v7h
Type: github-advisory

## Affected
- PyPI: `Scrapy` — affected >=0 <2.11.2

## Details
### Impact

Scrapy was following redirects regardless of the URL protocol, so redirects were working for `data://`, `file://`, `ftp://`, `s3://`, and any other scheme defined in the `DOWNLOAD_HANDLERS` setting.

However, HTTP redirects should only work between URLs that use the `http://` or `https://` schemes.

A malicious actor, given write access to the start requests (e.g. ability to define `start_urls`) of a spider and read access to the spider output, could exploit this vulnerability to:
- Redirect to any local file using the `file://` scheme to read its contents.
- Redirect to an `ftp://` URL of a malicious FTP server to obtain the FTP username and password configured in the spider or project.
- Redirect to any `s3://` URL to read its content using the S3 credentials configured in the spider or project.

For `file://` and `s3://`, how the spider implements its parsing of input data into an output item determines what data would be vulnerable. A spider that always outputs the entire contents of a response would be completely vulnerable, while a spider that extracted only fragments from the response could significantly limit vulnerable data.

### Patches

Upgrade to Scrapy 2.11.2.

### Workarounds

Replace the built-in retry middlewares (`RedirectMiddleware` and `MetaRefreshMiddleware`) with custom ones that implement the fix from Scrapy 2.11.2, and verify that they work as intended.

### References

This security issue was reported by @mvsantos at https://github.com/scrapy/scrapy/issues/457.

## References
- https://github.com/scrapy/scrapy/security/advisories/GHSA-23j4-mw76-5v7h
- https://github.com/scrapy/scrapy/issues/457
- https://github.com/scrapy/scrapy/commit/36287cb665ab4b0c65fd53181c9a0ef04990ada6
- https://github.com/scrapy/scrapy
