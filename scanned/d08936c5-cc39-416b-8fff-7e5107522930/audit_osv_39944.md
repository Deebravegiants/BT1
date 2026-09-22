# [C] CVE-2026-48689

## Summary
Severity: Critical
Advisory: CVE-2026-48689
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-48689
Type: osv

## Details
FastNetMon Community Edition through 1.2.9 contains an off-by-one heap-based buffer overflow in the dynamic_binary_buffer_t class (src/dynamic_binary_buffer.hpp). Five methods (append_dynamic_buffer, append_data_as_pointer, append_data_as_object_ptr, memcpy_from_ptr, memcpy_from_object_ptr) use an incorrect bounds check of the form 'if (offset + length > maximum_internal_storage_size + 1)' instead of the correct 'if (offset + length > maximum_internal_storage_size)'. This allows writing exactly one byte past the end of the heap-allocated buffer. The class is used pervasively in BGP message encoding/decoding, NetFlow template processing, and Flow Spec NLRI construction. An attacker who can send network traffic (NetFlow, sFlow, IPFIX, or BGP) to a FastNetMon instance can trigger this overflow, potentially achieving arbitrary code execution by corrupting heap metadata. Notably, the append_byte() method uses the correct bounds check, confirming the inconsistency.

## References
- https://github.com/pavel-odintsov/fastnetmon/blob/master/src/dynamic_binary_buffer.hpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48689.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48689
- https://github.com/pavel-odintsov/fastnetmon
- https://lorikeetsecurity.com/blog/fastnetmon-cve-2026-48689-dynamic-buffer-off-by-one
