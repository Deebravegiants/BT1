# [M] CVE-2025-60458

## Summary
Severity: Medium
Advisory: CVE-2025-60458
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2025-60458
Type: osv

## Details
UxPlay 1.72 contains a double free vulnerability in its RTSP request handling. A specially crafted RTSP TEARDOWN request can trigger multiple calls to free() on the same memory address, potentially causing a Denial of Service.

## References
- https://github.com/0pepsi/CVE-2025-60458
