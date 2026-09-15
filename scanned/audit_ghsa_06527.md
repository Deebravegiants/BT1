# [C] lettre has TLS hostname verification disabled when using Boring TLS backend

## Summary
Severity: Critical
Advisory: GHSA-4pj9-g833-qx53
CVE: CVE-2026-46428
CWE: CWE-295
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-4pj9-g833-qx53
Type: github-advisory

## Affected
- crates.io: `lettre` — affected >=0.10.1 <0.11.22

## Details
### Summary
An inverted-boolean bug in lettre's `boring-tls` integration silently
disables TLS hostname verification for callers using the default (strict)
configuration. An on-path attacker presenting any chain-valid certificate
for any domain can intercept SMTP submission, including PLAIN/LOGIN
credentials and message contents, against any lettre user built with the
`boring-tls` feature. Other TLS backends (`native-tls`, `rustls`) are
unaffected.

### Details
boring's `SslConnectorBuilder::set_verify_hostname(bool)` /
`verify_hostname(bool)` API takes a *verify* flag — `true` means enforce
hostname verification, `false` means skip it. (Boring docs:
https://docs.rs/boring/latest/boring/ssl/struct.ConnectConfiguration.html#method.set_verify_hostname)
lettre's `TlsParametersBuilder` exposes the opposite-named flag
`accept_invalid_hostnames: bool` — `true` means *accept invalid* (skip
verification), `false` means verify. lettre passes this flag directly to
boring at both TLS-upgrade sites, inverting the semantics:
src/transport/smtp/client/net.rs:202 (sync)
    .verify_hostname(*accept_invalid_hostnames)
src/transport/smtp/client/async_net.rs:377 (async)
    config.set_verify_hostname(accept_invalid_hostnames);
Concrete behaviour under `boring-tls`:
  * accept_invalid_hostnames = false  (the strict default)
      → set_verify_hostname(false)  → hostname verification SKIPPED
        (wrong; the caller asked for strict verification)
  * accept_invalid_hostnames = true   (explicit opt-in to "dangerous")
      → set_verify_hostname(true)   → hostname verification ENFORCED
        (wrong; the caller opted into accepting any name)
Boring's own warning on `set_verify_hostname`:
    "If hostname verification is not used, *any* valid certificate for
    *any* site will be trusted for use from any other. This introduces
    a significant vulnerability to man-in-the-middle attacks."
`native-tls` (src/transport/smtp/client/tls.rs:355) uses
`danger_accept_invalid_hostnames(self.accept_invalid_hostnames)`, whose
flag name and semantics match lettre's — unaffected. `rustls` uses a
separate verifier path — unaffected.
The bug was introduced in PR #797 ("Add support for boring TLS"), commit
985fa7e, first released in v0.10.1, and persists unchanged through v0.11.21
(latest). Zero existing tests cover `accept_invalid_hostnames` end-to-end
with any backend, which is why the inversion has gone undetected.
Fix: negate the flag at both call sites. Two-line patch:
    -    .verify_hostname(*accept_invalid_hostnames)
    +    .verify_hostname(!*accept_invalid_hostnames)
    -    config.set_verify_hostname(accept_invalid_hostnames);
    +    config.set_verify_hostname(!accept_invalid_hostnames);
I have the patch ready locally and can push to a private fork if a
collaborative fix branch is preferred.

### PoC
Setup (any lettre version >= v0.10.1, built with the `boring-tls`
feature, default-strict configuration):
1. Generate a TLS cert for any hostname the attacker controls, e.g.
   `attacker.example`, signed by any CA in the client's trust store
   (e.g. a Let's Encrypt cert is sufficient).
2. Stand up an attacker SMTP server on the network path between the
   lettre client and the intended MX. Have it present the
   `attacker.example` cert on STARTTLS or implicit TLS.
3. Use lettre with default-strict TLS to send to the real MX hostname,
   e.g. `mail.example.com`:
       use lettre::transport::smtp::client::{Tls, TlsParameters};
       use lettre::{AsyncSmtpTransport, Tokio1Executor, Message};
       let tls = TlsParameters::builder("mail.example.com".to_owned())
           .build_boring()
           .unwrap();
       let mailer = AsyncSmtpTransport::<Tokio1Executor>::relay(
               "mail.example.com",
           )?
           .tls(Tls::Required(tls))
           .build();
       mailer.send(message).await?;     // succeeds against attacker
Expected with hostname verification: handshake fails because the
presented leaf cert's SAN does not match `mail.example.com`.
Actual on `boring-tls`: handshake succeeds. lettre proceeds with the
SMTP transaction, sending MAIL FROM, RCPT TO, message body, and any
configured SMTP AUTH credentials to the attacker.
Symmetric inverse PoC (proves the inversion, not just a missing check):
configure `.dangerous_accept_invalid_hostnames(true)` and try to connect
to a server whose cert SAN matches the connect domain. With the bug,
the handshake *fails* because lettre passes `true` to `verify_hostname`
and boring rejects... actually wait, it succeeds (SAN matches). Better
inverse demonstration: connect to a server whose cert SAN matches the
connect domain with `accept_invalid_hostnames=true`, then connect to a
mismatched-SAN server with the same flag — the latter is rejected,
proving the flag is inverted (the user opted into accepting any name,
yet lettre enforces strict verification).
A reproducer cargo project can be produced on request.

### Impact
Who is impacted: any lettre user who
  1. enables the `boring-tls` feature, AND
  2. relies on default-strict hostname verification
     (i.e. does NOT call `.dangerous_accept_invalid_hostnames(true)`).
This is the entire "I want strict TLS" population on `boring-tls`. They
get the opposite of what they asked for: a TLS handshake that ignores
hostname mismatch.
Exploitation: an attacker on the network path between the lettre client
and the target SMTP server, holding any chain-valid TLS certificate
(e.g. a free Let's Encrypt cert for a domain the attacker owns), can
present that certificate when the lettre client connects to the intended
MX. boring accepts the handshake, lettre proceeds, and the attacker
gains read/write access to:
  * SMTP envelope (MAIL FROM, RCPT TO)
  * Message bodies, attachments, headers
  * Any SMTP AUTH credentials (PLAIN, LOGIN, CRAM-MD5, etc.)
  * Any DKIM signatures and DMARC alignment downstream depends on
    can be inspected and selectively dropped
Confidentiality and integrity impact: High. Availability impact: None
direct (the attacker can choose to forward or drop, but the bug itself
does not deny service).
Cloudflare's email-fwdr independently identified and mitigated this
downstream by promoting a previously-metric-only post-handshake SAN
check to a hard error (fix landed 2026-05-12). Because we're mitigated
downstream, we are not on a publication clock; we are reporting so the
upstream fix can ship and other lettre+boring-tls deployments can stop
relying on per-caller workarounds. Happy to coordinate on embargo
timing.
Affected versions: every released lettre version with `boring-tls`
support, from v0.10.1 (PR #797, commit 985fa7e) through v0.11.21
(latest). No prior advisory or fix.
Suggested fix: two-line negation of the flag at the boring call sites
(see Details). Patch is ready locally and can be attached to a private
collaboration fork.

## References
- https://github.com/lettre/lettre/security/advisories/GHSA-4pj9-g833-qx53
- https://nvd.nist.gov/vuln/detail/CVE-2026-46428
- https://github.com/lettre/lettre/commit/f5efffc88360dbdbfcef80f465e42d5bce68ca35
- https://github.com/lettre/lettre
- https://github.com/lettre/lettre/releases/tag/v0.11.22
- https://rustsec.org/advisories/RUSTSEC-2026-0141.html
