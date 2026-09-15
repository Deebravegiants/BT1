# [M] Avahi has Uncontrolled Recursion in lookup_handle_cname function

## Summary
Severity: Medium
Advisory: CVE-2026-24401
Aliases: GHSA-h4vp-5m8j-f6w3
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-24
Source: https://osv.dev/vulnerability/CVE-2026-24401
Type: osv

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. In versions 0.9rc2 and below, avahi-daemon can be crashed via a segmentation fault by sending an unsolicited mDNS response containing a recursive CNAME record, where the alias and canonical name point to the same domain (e.g., "h.local" as a CNAME for "h.local"). This causes unbounded recursion in the lookup_handle_cname function, leading to stack exhaustion. The vulnerability affects record browsers where AVAHI_LOOKUP_USE_MULTICAST is set explicitly, which includes record browsers created by resolvers used by nss-mdns. This issue is patched in commit 78eab31128479f06e30beb8c1cbf99dd921e2524.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24401.json
- https://github.com/avahi/avahi/security/advisories/GHSA-h4vp-5m8j-f6w3
- https://nvd.nist.gov/vuln/detail/CVE-2026-24401
- https://github.com/avahi/avahi/issues/501
- https://github.com/avahi/avahi/commit/78eab31128479f06e30beb8c1cbf99dd921e2524
