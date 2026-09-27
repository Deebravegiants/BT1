# [C] OpenSIPS: Stack Buffer Overflow in sip_to_json() Header Name Copy

## Summary
Severity: Critical
Advisory: CVE-2026-45538
Aliases: GHSA-37wc-5j8j-95x3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-45538
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. In versions 4.0.0 and prior, processing a SIP message with a header name longer than 255 bytes causes a stack buffer overflow when sip_to_json() is called in the routing script. Function sip_to_json() (modules/sipmsgops/sipmsgops.c) copies SIP header names into a fixed 255-byte stack buffer without bounds checking, performing a memcpy of the full header-name length even though the SIP parser imposes no such limit (a header name can be roughly 65000 bytes). As a result, when a routing script calls sip_to_json(), a SIP message with a header name longer than 255 bytes triggers a stack buffer overflow in which both the length and content of the overwrite are attacker-controlled, corrupting the saved frame pointer and return address. A single unauthenticated UDP packet to the SIP port (5060) can crash the process or, on builds without stack protections, hijack the return address to achieve remote code execution. This affects deployments whose routing script invokes sip_to_json(). This issue was not fixed at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45538.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-37wc-5j8j-95x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45538
