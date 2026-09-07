# [M] aiosmtplib: STARTTLS response injection

## Summary
Severity: Medium
Advisory: GHSA-vxj7-4xrp-5vr4
CVE: CVE-2026-55558
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-27
Source: https://github.com/advisories/GHSA-vxj7-4xrp-5vr4
Type: github-advisory

## Affected
- PyPI: `aiosmtplib` — affected >=0 <5.1.2

## Details
## Impact

When a connection is upgraded with STARTTLS, aiosmtplib reads the server's 220 go-ahead reply and immediately performs the TLS handshake without discarding any data still sitting in the receive buffer. Bytes the protocol read off the plaintext socket before the handshake survive across the plaintext→TLS boundary (the asyncio transport is swapped in place, so the protocol object and its buffer are reused), and are then parsed as though they had arrived inside the TLS session.

Who is affected: Any caller that uses STARTTLS by passing `start_tls=True` or `start_tls=None` when the server advertises STARTTLS, and whose traffic can be intercepted by an active network attacker on the plaintext leg of the connection.

A man in the middle can send, in a single segment immediately after the client's STARTTLS command, the 220 reply followed by attacker-chosen response lines (e.g. 220 Go ahead\r\n250-mx.evil\r\n250 AUTH LOGIN\r\n). aiosmtplib
  consumes only the 220, leaves the injected lines buffered, completes the handshake, and then parses the attacker's pre-staged plaintext as the first post-TLS server response. This also desynchronizes every
  subsequent command/response pair inside the "encrypted" session.

Not affected: Connections using implicit/direct TLS (`use_tls=True`) have no plaintext phase and are not vulnerable. The attack requires an active man in the middle via network compromise; a passive eavesdropper cannot exploit it.


# Patches

  A fix is available in aiosmtplib 5.1.2. All earlier versions that support STARTTLS are affected; upgrade to 5.1.2 or
  later.

  The fix treats any data buffered after the 220 STARTTLS reply and before the handshake as a protocol violation, per RFC 3207 §4.2 ("the client MUST discard any knowledge obtained from the server … which was not
  obtained from the TLS negotiation itself").

# Workarounds

  If you cannot upgrade immediately:

  - Use implicit TLS instead of STARTTLS. Connect with `use_tls=True`. This removes the plaintext phase entirely.
  - If STARTTLS is unavoidable, restrict connections to servers reached over a trusted network path.

## References
- https://github.com/cole/aiosmtplib/security/advisories/GHSA-vxj7-4xrp-5vr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55558
- https://github.com/cole/aiosmtplib/commit/9fab7ba1361dbf7622ede1315a24be805cff09c9
- https://github.com/cole/aiosmtplib
- https://github.com/cole/aiosmtplib/releases/tag/v5.1.2
