# [M] ZeptoClaw: Email Sender Spoofing to bypass Header-Only From Allowlist Validation

## Summary
Severity: Medium
Advisory: GHSA-4cm8-xpfv-jv6f
CWE: CWE-306, CWE-345
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-4cm8-xpfv-jv6f
Type: github-advisory

## Affected
- crates.io: `zeptoclaw` — affected >=0 <0.7.6

## Details
### Summary
The email channel authorizes senders based on the parsed `From` header identity only. If upstream email authentication/enforcement is weak (for example, relaxed SPF/DKIM/DMARC handling), an attacker can spoof an allowlisted sender address and have the message treated as trusted input. 

### Details
Relevant code paths:

- `src/channels/email_channel.rs:311` extracts sender identity from parsed message headers:
  - `let from = parsed.from() ... a.address() ...`
- `src/channels/email_channel.rs:328` authorizes using that `from` value:
  - `if !self.is_sender_allowed(&from) { ... }`
- `src/channels/email_channel.rs:87` onward (`is_sender_allowed`) performs allowlist/domain matching against the same header-derived value.
- There is no in-channel validation of sender authenticity indicators such as SPF/DKIM/DMARC results before allowlist trust decisions.

Result:
- Trust decision is based on a potentially spoofable header field unless mailbox/provider-side anti-spoofing controls are strong and enforced.

### PoC
1. Configure email channel with strict sender allowlist:
   - `channels.email.enabled = true`
   - `channels.email.allowed_senders = ["ceo@example.com"]`
   - `channels.email.deny_by_default = true`
2. Ensure the monitored mailbox accepts or forwards a spoofed message (for testing, use a local SMTP path that does not enforce sender authentication strongly).
3. Send an email to the monitored inbox with forged header identity:

```bash
python - <<'PY'
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["From"] = "ceo@example.com"   # forged trusted sender
msg["To"] = "bot-inbox@example.net"
msg["Subject"] = "forged control message"
msg.set_content("FORGED EMAIL CONTENT")

# Example test SMTP endpoint
with smtplib.SMTP("127.0.0.1", 25) as s:
    s.send_message(msg)
PY
```

4. Wait for IMAP fetch/IDLE processing.
5. Observe the message is accepted as allowlisted sender `ceo@example.com` and published as inbound channel input.

### Impact
- Vulnerability type: sender identity spoofing risk due to header-based authorization.
- Affected deployments: those using email channel allowlists where upstream anti-spoof controls are weak, misconfigured, or bypassed.
- Security effect:
  - Spoofed `From` headers may bypass logical sender allowlist.
  - Malicious content can enter trusted automation/agent flows as if sent by authorized identities.
- Risk is reduced in environments with strict SPF/DKIM/DMARC enforcement and strong inbound mail hygiene, but not eliminated at application layer.

### Patch Recommendation
Add a sender-authentication gate in `src/channels/email_channel.rs` immediately after parsing `from` (`src/channels/email_channel.rs:311`) and before allowlist enforcement (`src/channels/email_channel.rs:328`). The gate should require trusted SPF/DKIM/DMARC evidence with domain alignment (for example, `DMARC=pass`, or aligned SPF/DKIM pass) before `is_sender_allowed` is evaluated. For backward compatibility, add a configurable mode in `EmailConfig` (for example, `sender_verification_mode`), but recommend hardened settings in production: `dmarc_aligned`, exact-address allowlists, and `deny_by_default=true`.

## References
- https://github.com/qhkm/zeptoclaw/security/advisories/GHSA-4cm8-xpfv-jv6f
- https://github.com/qhkm/zeptoclaw
- https://github.com/qhkm/zeptoclaw/releases/tag/v0.7.6
