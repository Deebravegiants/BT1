# [M] Denial of Service in CivetWeb

## Summary
Severity: Medium
Advisory: CVE-2025-9648
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-9648
Type: osv

## Details
A vulnerability in the CivetWeb library's function mg_handle_form_request allows remote attackers to trigger a denial of service (DoS) condition. By sending a specially crafted HTTP POST request containing a null byte in the payload, the server enters an infinite loop during form data parsing. Multiple malicious requests will result in complete CPU exhaustion and render the service unresponsive to further requests.

This issue was fixed in commit 782e189. This issue affects only the library, standalone executable pre-built by vendor is not affected.

## References
- https://cert.pl/en/posts/2025/09/CVE-2025-9648
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9648.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9648
- https://github.com/civetweb/civetweb/issues/1348
- https://github.com/civetweb/civetweb/commit/782e18903515f43bafbf2e668994e82bdfa51133
- https://github.com/civetweb/civetweb
