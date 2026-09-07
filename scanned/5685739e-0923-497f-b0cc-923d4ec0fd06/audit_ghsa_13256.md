# [M] matrix-media-repo: Unsafe media served inline on download endpoints

## Summary
Severity: Medium
Advisory: GHSA-5crw-6j7v-xc72
CVE: CVE-2023-41318
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-08
Source: https://github.com/advisories/GHSA-5crw-6j7v-xc72
Type: github-advisory

## Affected
- Go: `github.com/turt2live/matrix-media-repo` — affected >=0 <1.3.0

## Details
### Impact
A malicious user can upload an SVG image containing JavaScript to their server. When matrix-media-repo is asked to serve that media via the `/_matrix/media/(r0|v3)/download` endpoint, it would be served with a `Content-Disposition` of `inline`. This can allow JavaScript to run in the browser if a client links to the `/download` endpoint directly.

Server operators which do not share a domain between matrix-media-repo and other services are not affected, but are encouraged to upgrade regardless.

### Patches
https://github.com/turt2live/matrix-media-repo/commit/77ec2354e8f46d5ef149d1dcaf25f51c04149137 and https://github.com/turt2live/matrix-media-repo/commit/bf8abdd7a5371118e280c65a8e0ec2b2e9bdaf59 fix the issue. Operators should upgrade to v1.3.0 as soon as possible.

### Workarounds
The `Content-Disposition` header can be overridden by the reverse proxy in front of matrix-media-repo to always use `attachment`, defeating this issue at the cost of "worse" user experience when clicking download links.

### References
https://developer.mozilla.org/en-US/docs/Web/SVG/Element/script

## References
- https://github.com/turt2live/matrix-media-repo/security/advisories/GHSA-5crw-6j7v-xc72
- https://nvd.nist.gov/vuln/detail/CVE-2023-41318
- https://github.com/turt2live/matrix-media-repo/commit/77ec2354e8f46d5ef149d1dcaf25f51c04149137
- https://github.com/turt2live/matrix-media-repo/commit/bf8abdd7a5371118e280c65a8e0ec2b2e9bdaf59
- https://developer.mozilla.org/en-US/docs/Web/SVG/Element/script
- https://github.com/turt2live/matrix-media-repo
