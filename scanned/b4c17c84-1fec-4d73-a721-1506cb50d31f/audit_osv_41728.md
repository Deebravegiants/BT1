# [M] FreeRDP: Double-free of `client_formats` in the rdpsnd server channel on a malformed Client Audio Formats PDU

## Summary
Severity: Medium
Advisory: CVE-2026-63652
Aliases: GHSA-9g22-w2gr-vcmp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-63652
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.28.0, rdpsnd_server_recv_formats in channels/rdpsnd/server/rdpsnd_main.c frees context->client_formats on a malformed Client Audio Formats PDU without clearing the owning pointer or num_client_formats. An authenticated RDP client can trigger an error such as a cbSize larger than the remaining record, leave the dangling pointer in the server context, and cause rdpsnd_server_context_free to free the same allocation again at session teardown. This reliably terminates the server and can create allocator-dependent heap corruption. This issue is fixed in version 3.28.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63652.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-9g22-w2gr-vcmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-63652
- https://github.com/FreeRDP/FreeRDP/commit/caf653c0ba1c75ec8f298d1baa59770102a5d14c
- https://github.com/FreeRDP/FreeRDP/pull/12993
