# [M] SSRF via image import from URL allows internal network probing by authenticated users

## Summary
Severity: Medium
Advisory: CVE-2026-28385
Aliases: GHSA-3gq2-x4qg-p4g6
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-28385
Type: osv

## Details
In Canonical LXD versions 4.12 through 6.9, a Server-Side Request Forgery (SSRF) vulnerability in the image import functionality allows authenticated users with the can_create_images entitlement to interact with internal network infrastructure via the /images endpoint. When importing an image from a URL source, the LXD daemon fails to validate or restrict outbound destination IP addresses, allowing connections to loopback, RFC1918 private ranges, and cloud metadata endpoints. This enables error-based port scanning and unauthorized interaction with internal HTTP services from the daemon's network position.

## References
- https://github.com/canonical
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28385.json
- https://github.com/canonical/lxd/security/advisories/GHSA-3gq2-x4qg-p4g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-28385
- https://github.com/canonical/lxd/pull/18462
- https://github.com/canonical/lxd
