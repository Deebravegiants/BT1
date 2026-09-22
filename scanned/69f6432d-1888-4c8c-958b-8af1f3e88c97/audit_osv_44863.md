# [H] Out-of-bounds write in DTLS peer Connection ID getsockopt (`TLS_DTLS_PEER_CID_VALUE`) in Zephyr net sockets/TLS

## Summary
Severity: High
Advisory: CVE-2026-8718
Aliases: GHSA-p3r6-mx6c-33gq
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-8718
Type: osv

## Details
tls_opt_dtls_peer_connection_id_value_get() in subsys/net/lib/sockets/sockets_tls.c, which handles getsockopt(SOL_TLS, TLS_DTLS_PEER_CID_VALUE), passed the caller-supplied optval directly to mbedtls_ssl_get_peer_cid() without verifying the buffer was at least MBEDTLS_SSL_CID_OUT_LEN_MAX (default 32) bytes. mbedtls_ssl_get_peer_cid() copies the peer-negotiated DTLS Connection ID (length 1..MBEDTLS_SSL_CID_OUT_LEN_MAX) into that buffer without a destination-size parameter, so a caller-supplied optlen smaller than the CID causes a write of up to 31 bytes past the buffer end.

In CONFIG_USERSPACE builds the getsockopt syscall verifier (z_vrfy_zsock_getsockopt) bounce-buffers the user's optval into a kernel allocation of exactly optlen bytes (k_usermode_alloc_from_copy -> z_thread_malloc), so an unprivileged user thread that passes a small optlen on a connected DTLS socket with Connection ID enabled induces a kernel-heap buffer overflow, with the overflowing content being the remote peer's CID.

The defect requires CONFIG_MBEDTLS_SSL_DTLS_CONNECTION_ID, an established DTLS session with a negotiated peer CID, and (for the kernel-crossing case) CONFIG_USERSPACE. Introduced when the TLS_DTLS_CID option was added (v3.5.0).

The fix rejects callers whose optlen is below MBEDTLS_SSL_CID_OUT_LEN_MAX with -EINVAL.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8718.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-p3r6-mx6c-33gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-8718
- https://github.com/zephyrproject-rtos/zephyr/commit/aa317825a55a401315e8e17f620c70c02e8f176d
- https://github.com/zephyrproject-rtos/zephyr
