# [H] Unterminated URI buffer causes out-of-bounds read in LwM2M firmware pull (Package URI)

## Summary
Severity: High
Advisory: CVE-2026-10672
Aliases: GHSA-rf6j-4mpp-j9mf
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-10672
Type: osv

## Details
subsys/net/lib/lwm2m/lwm2m_pull_context.c copied the firmware-update Package URI into a fixed static buffer (context.uri, size CONFIG_LWM2M_SWMGMT_PACKAGE_URI_LEN, default 128) with memcpy(context.uri, uri, LWM2M_PACKAGE_URI_LEN), copying exactly the destination size with no length validation. The Firmware-Update object stores the server-supplied Package URI (/5/0/1) in a 255-byte buffer, so a LwM2M management server (or an on-path attacker on a session lacking strong DTLS) can WRITE a URI of 128-254 characters; only the first 128 bytes are then copied into context.uri with no NUL terminator. That buffer is subsequently consumed as a C string by http_parser_parse_url(context.uri, strlen(context.uri), ...), strlen-based CoAP URI-path/PROXY-URI option appends, and lwm2m_parse_peerinfo(), causing an out-of-bounds read of adjacent static memory. The over-read bytes are appended to outbound CoAP requests (information disclosure of adjacent device memory to the server/proxy) and can crash the device (denial of service). The vulnerable copy was introduced by the pull-context refactor (first released in v3.0.0) and is present through v4.4.0; the default-on CONFIG_LWM2M_FIRMWARE_UPDATE_PULL_SUPPORT path is affected. The fix adds a strlen(uri) >= sizeof(context.uri) check returning -ENOMEM and switches to strcpy(), guaranteeing a bounded, NUL-terminated buffer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10672.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-rf6j-4mpp-j9mf
- https://nvd.nist.gov/vuln/detail/CVE-2026-10672
- https://github.com/zephyrproject-rtos/zephyr/commit/99a164df5cea5af76e32b57c6d51854f018969a2
- https://github.com/zephyrproject-rtos/zephyr
