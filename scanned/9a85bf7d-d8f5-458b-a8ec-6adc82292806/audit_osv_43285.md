# [M] RustDesk < 1.4.7 Uncontrolled Memory Allocation DoS via BytesCodec

## Summary
Severity: Medium
Advisory: CVE-2026-73108
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-73108
Type: osv

## Details
RustDesk versions before 1.4.7 contain an uncontrolled speculative memory allocation vulnerability in BytesCodec. Before authentication, the decoder trusts the payload length encoded in a four-byte frame header and reserves that amount before receiving the payload. A crafted header can request up to 1,073,741,823 bytes of capacity, allowing unauthenticated attackers to use concurrent TCP connections to cause memory exhaustion and denial of service. The fix caps header-triggered speculative preallocation at 256 KiB.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73108.json
- https://github.com/rustdesk/rustdesk/releases/tag/1.4.7
- https://nvd.nist.gov/vuln/detail/CVE-2026-73108
- https://www.vulncheck.com/advisories/rustdesk-uncontrolled-memory-allocation-dos-via-bytescodec
- https://github.com/rustdesk/hbb_common/commit/547da54b4ee58eed47163fbd47edb4639e3d88de
- https://github.com/rustdesk/rustdesk/commit/518296f2570d107ad416f29ade5fcce3177f4115
- https://github.com/rustdesk/rustdesk
