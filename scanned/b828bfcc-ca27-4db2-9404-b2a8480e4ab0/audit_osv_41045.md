# [M] PJSIP: Stack overflow handling Service-Route headers in a registration response

## Summary
Severity: Medium
Advisory: CVE-2026-57161
Aliases: GHSA-xc62-j9h2-mp84
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-57161
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to commit acc03b5, a stack buffer overflow exists in PJSUA when processing Service-Route headers in a registration response (update_service_route() in pjsua_acc.c). This affects applications that register using the PJSUA/PJSUA2 account API (the default registration path). The Service-Route URIs from a 2xx response to REGISTER are stored into a fixed-size array without bounding the number of headers; a registrar that returns an excessive number of Service-Route headers can write past the end of the array on the stack. The values written are internal pointers rather than arbitrary data, so the most likely impact is unexpected application termination (denial of service), though memory corruption cannot be excluded. The malicious response may come from a compromised or malicious registrar, or — over unprotected transports — a spoofed response. This issue has been patched via commit acc03b5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57161.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-xc62-j9h2-mp84
- https://nvd.nist.gov/vuln/detail/CVE-2026-57161
- https://github.com/pjsip/pjproject/commit/acc03b57cef7a7d31b8e1f5b9117437d7e87c591
