# [M] OctoPrint Vulnerable to Denial of Service through malformed HTTP request in OctoPrint

## Summary
Severity: Medium
Advisory: GHSA-9wj4-8h85-pgrw
CVE: CVE-2025-48879
CWE: CWE-140, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-9wj4-8h85-pgrw
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.11.2

## Details
### Impact

OctoPrint versions up until and including 1.11.1 contain a vulnerability that allows any unauthenticated attacker to send a manipulated broken `multipart/form-data` request to OctoPrint and through that make the web server component become unresponsive. This could be used to effectively run a denial of service attack on the OctoPrint server.

### Patches

The vulnerability has been patched in version 1.11.2.

### Workaround

OctoPrint administrators are once more reminded to not make OctoPrint available on hostile networks (e.g. the internet), regardless of whether this vulnerability is patched or not.

### Details

The issue can be triggered by a broken `multipart/form-data` request lacking an end boundary to any of OctoPrint's endpoints implemented through the `octoprint.server.util.tornado.UploadStorageFallbackHandler` request handler. The request handler will get stuck in an endless busy loop, looking for a part of the request that will never come. As Tornado is single-threaded, that will effectively block the whole web server.

The fix adds detection of invalid requests like that and ensures they are handled gracefully with an HTTP 400 Bad Request response.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi.

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-9wj4-8h85-pgrw
- https://nvd.nist.gov/vuln/detail/CVE-2025-48879
- https://github.com/OctoPrint/OctoPrint/commit/c9c35c17bd820f19c6b12e6c0359fc0cfdd0c1ec
- https://github.com/OctoPrint/OctoPrint
