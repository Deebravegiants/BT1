# [H] Heap out-of-bounds write in Zephyr hawkBit OTA client when terminating server response body

## Summary
Severity: High
Advisory: CVE-2026-10849
Aliases: GHSA-39h3-7phx-pwhv
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-10849
Type: osv

## Details
The hawkBit device management client in subsys/mgmt/hawkbit accumulates the body of an HTTP response from the update server into a heap buffer in response_json_cb() (subsys/mgmt/hawkbit/hawkbit.c). The buffer is sized to hold the received body bytes but reserves no space for a terminating NUL. When the full response has arrived, the code writes response_data[downloaded_size] = '\0' — and whenever the accumulated body length equals the allocation, that terminator lands one byte past the end of the heap object (a heap-based out-of-bounds write, CWE-122 / CWE-787).

The body length and fragmentation are taken directly from the parsed HTTP response (rsp->body_frag_start / rsp->body_frag_len) and are fully controlled by the remote hawkBit server, which chooses its own response length. The precise trigger depends on how the buffer grows, and both forms are remotely reachable. Since v4.0.0 the reallocation is sized to exactly downloaded_size + body_len, so any response body larger than the 1100-byte initial buffer makes the out-of-bounds write deterministic; such response sizes are normal for hawkBit deployment metadata. Before v4.0.0 the buffer grew by doubling and the growth check ((downloaded_size + body_len) > response_buffer_size) is false at equality, so a response body whose length is exactly the current allocation — 1100 bytes with the default initial buffer — skips the reallocation entirely and writes the terminator at response_data[1100] of an 1100-byte object. The HTTP length-mismatch check does not catch this, because the declared and received lengths genuinely agree. Either form is reachable by a malicious, compromised, or man-in-the-middle update server (TLS is optional and, when enabled, does not protect against a hostile server), with no authentication of response content and no client-side length cap protecting the write.

The out-of-bounds write is a fixed single NUL byte immediately following the allocation, corrupting adjacent allocator metadata or the next allocation. The practical impact is heap corruption leading to denial of service (fault on a subsequent allocation or free), with the bounded, allocator-dependent possibility of further corruption. The fix sizes the buffer to the body length plus one and copies with memcpy, ensuring the terminator always lands within the allocation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10849.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-39h3-7phx-pwhv
- https://nvd.nist.gov/vuln/detail/CVE-2026-10849
- https://github.com/zephyrproject-rtos/zephyr/commit/59d7ab58d853489e6134081cadb11733730264ac
- https://github.com/zephyrproject-rtos/zephyr
