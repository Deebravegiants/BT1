# [H] Bluetooth: L2CAP: validate option length before reading conf opt value

## Summary
Severity: High
Advisory: CVE-2026-64403
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64403
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: validate option length before reading conf opt value

l2cap_get_conf_opt() derives the option length from the
attacker-controlled opt->len field and immediately dereferences
opt->val (as u8, get_unaligned_le16() or get_unaligned_le32(), or a
raw pointer for the default case) before any caller has confirmed
that opt->len bytes are present in the buffer. The callers
(l2cap_parse_conf_req(), l2cap_parse_conf_rsp() and
l2cap_conf_rfc_get()) only detect a malformed option afterwards, once
the running length has gone negative, by which point the
out-of-bounds read has already executed.

An existing post-hoc length check keeps the garbage value from being
consumed, so this is not a data leak in the current control flow. It
is still a validate-after-use ordering bug: up to 4 bytes are read
past the end of the buffer before it is known to contain them, and it
is fragile to future changes in the callers.

Fix it at the source. Pass the end of the buffer into
l2cap_get_conf_opt() and refuse to touch opt->val unless the full
option (header + value) fits. Each caller computes an end pointer
once before the loop and checks the return value directly instead of
inferring the error from a negative length.

## References
- https://git.kernel.org/stable/c/687617555cedfb74c9e3cb85d759b908dcb17856
- https://git.kernel.org/stable/c/6b47bdaacfd0045687880177e0987055d8f4765a
- https://git.kernel.org/stable/c/73abbaf91aa33da87c008fb62c148ade561bb606
- https://git.kernel.org/stable/c/7d871e969b941ce25653f7716203a0ea4d07ad4b
- https://git.kernel.org/stable/c/98d93c226bdfaa79bbdd86981921d7f106374225
- https://git.kernel.org/stable/c/996d3da39899aceb8f4910911a3f19a45a7d9d1b
- https://git.kernel.org/stable/c/cca81b4bc672604a84f6d224a55cc77ec7dee619
- https://git.kernel.org/stable/c/f70d4aa88068096f35d73e3a05eff33c0a16b9cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64403.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
