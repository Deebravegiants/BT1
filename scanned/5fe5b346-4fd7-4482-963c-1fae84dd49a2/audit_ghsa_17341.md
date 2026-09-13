# [M] Portkey.ai Gateway: Server-Side Request Forgery (SSRF) in Custom Host

## Summary
Severity: Medium
Advisory: GHSA-hhh5-2cvx-vmfp
CVE: CVE-2025-66405
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-hhh5-2cvx-vmfp
Type: github-advisory

## Affected
- npm: `@portkey-ai/gateway` — affected >=0 <1.14.0

## Details
### Summary
The gateway determines the destination baseURL by prioritizing the value in the x-portkey-custom-host request header. The proxy route then appends the client-specified path to perform an external fetch. This can be maliciously used by users for SSRF (CWE-918) attack

### Impact
This vulnerability can be exploited to force the server to make requests to arbitrary hosts on the internal network. This could allow an attacker to exfiltrate sensitive data, for instance, by accessing the AWS metadata service.

### Patches
The issue is patched in 1.14.0 (https://github.com/Portkey-AI/gateway/pull/1372)

The vulnerability resides within the gateway's request processing function which handles the `x-portkey-custom-host` header. This parameter was passed directly or with insufficient validation/sanitization to an internal HTTP request function.

**The fix (v1.14.0) implements a robust allow-list policy:**

1. All custom host inputs are now strictly validated to ensure the resulting URI points only to trusted, expected external services.

2. The implementation now explicitly blocks requests to non-routable IP addresses, loopback addresses, private networks and standard metadata endpoints.

### Credit
This vulnerability was discovered and reported responsibly by @im-soohyun. We thank them for their adherence to coordinated vulnerability disclosure principles.

### References
https://cwe.mitre.org/data/definitions/918.html

## References
- https://github.com/Portkey-AI/gateway/security/advisories/GHSA-hhh5-2cvx-vmfp
- https://nvd.nist.gov/vuln/detail/CVE-2025-66405
- https://github.com/Portkey-AI/gateway/pull/1372
- https://github.com/Portkey-AI/gateway/commit/b5a7825ba5f4e6918deb32d9969899ce2229a885
- https://github.com/Portkey-AI/gateway
