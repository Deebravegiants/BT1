# [M] MISP Insufficient Outbound URL Validation Allows SSRF and Credential Disclosure via Feed Redirects and TAXII Discovery

## Summary
Severity: Medium
Advisory: CVE-2026-86419
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:L/VA:H/SC:H/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86419
Type: osv

## Details
Affected versions of MISP contain insufficient validation of server-side outbound HTTP destinations in feed retrieval and TAXII discovery functionality.


In feed processing, redirects were followed without validating the redirect scheme or destination. The original request headers were reused across redirect hops, meaning authentication headers or API credentials configured for a feed could be forwarded to a different host. Redirects could also target internal network resources, resulting in SSRF. The fix adds redirect validation, blocks internal destinations for cross-host redirects, strips configured feed credentials before following redirects to another host, and pins validated DNS results to prevent re-resolution after validation.


The TAXII discovery endpoint had a related incomplete SSRF defense. It used gethostbyname() and compared the result against only a few literal addresses. This missed cases including IPv6 loopback (::1), numeric host encodings such as 0x7f000001, and potentially multiple DNS records. The fix moves TAXII discovery to the shared URL egress validator.


Together, these commits harden MISP's outbound URL handling against alternate-address representations, DNS-related bypasses, unsafe redirects, internal-host access, and cross-host credential forwarding.






Version affected: ≤2.5.45

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86419.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86419
- https://github.com/MISP/MISP/commit/06f541dcf
- https://github.com/MISP/MISP/commit/08d6efe24
- https://github.com/MISP/MISP
