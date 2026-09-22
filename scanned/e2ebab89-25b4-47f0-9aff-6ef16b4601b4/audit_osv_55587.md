# [M] CVE-2025-9901

## Summary
Severity: Medium
Advisory: CVE-2025-9901
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-9901
Type: osv

## Details
A flaw was found in libsoup’s caching mechanism, SoupCache, where the HTTP Vary header is ignored when evaluating cached responses. This header ensures that responses vary appropriately based on request headers such as language or authentication. Without this check, cached content can be incorrectly reused across different requests, potentially exposing sensitive user information. While the issue is unlikely to affect everyday desktop use, it could result in confidentiality breaches in proxy or multi-user environments.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2392790
- https://access.redhat.com/security/cve/CVE-2025-9901
