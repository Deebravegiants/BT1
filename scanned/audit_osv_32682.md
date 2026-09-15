# [M] libcoap Stack-Based Buffer Overflow in Address Resolution DoS or Potential RCE

## Summary
Severity: Medium
Advisory: CVE-2025-34468
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-31
Source: https://osv.dev/vulnerability/CVE-2025-34468
Type: osv

## Details
libcoap versions up to and including 4.3.5, prior to commit 30db3ea, contain a stack-based buffer overflow in address resolution when attacker-controlled hostname data is copied into a fixed 256-byte stack buffer without proper bounds checking. A remote attacker can trigger a crash and potentially achieve remote code execution depending on compiler options and runtime memory protections. Exploitation requires the proxy logic to be enabled (i.e., the proxy request handling code path in an application using libcoap).

## References
- https://libcoap.net/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34468.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34468
- https://www.vulncheck.com/advisories/libcoap-stack-based-buffer-overflow-in-address-resolution-dos-or-potential-rce
- https://github.com/obgm/libcoap/pull/1737
- https://github.com/obgm/libcoap/commit/30db3ea
- https://github.com/obgm/libcoap
