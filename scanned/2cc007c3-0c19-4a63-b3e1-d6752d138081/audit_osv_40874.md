# [M] Renesas TSIP TLS 1.3 transcript buffer out-of-bounds write in tsip_StoreMessage

## Summary
Severity: Medium
Advisory: CVE-2026-55958
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55958
Type: osv

## Details
Out-of-bounds write in the Renesas TSIP TLS 1.3 transcript buffer. In tsip_StoreMessage() the capacity check guarding the fixed message bag (MSGBAG_SIZE) sets an error code but fails to return, so execution falls through to an XMEMCPY that writes past the end of the buffer once the accumulated TLS 1.3 handshake transcript exceeds MSGBAG_SIZE (8 KB), corrupting adjacent heap state and potentially causing a remote denial of service crash. The bag is sized to hold a normal handshake, so this is reached only by an unusually large but valid certificate chain, or by a malicious or man-in-the-middle server sending an oversized handshake message to a client that does not strictly verify the chain. This only affects builds using the Renesas TSIP TLS port (WOLFSSL_RENESAS_TSIP_TLS) as a TLS 1.3 client on Renesas MCUs with TSIP hardware enabled, and is rated High within those builds. All other configurations are unaffected.

## References
- https://www.wolfssl.com/docs/security-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55958.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55958
- https://github.com/wolfSSL/wolfssl/pull/10705
- https://github.com/wolfSSL/wolfssl
