# [M] Prefix Truncation Attack against ChaCha20-Poly1305 and Encrypt-then-MAC aka Terrapin

## Summary
Severity: Medium
Advisory: GHSA-45x7-px36-x8w8
CVE: CVE-2023-48795
CWE: CWE-345, CWE-354
Ecosystem: Go, PyPI, crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-45x7-px36-x8w8
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.40.2
- Go: `golang.org/x/crypto` — affected >=0.1.0 <0.17.0
- PyPI: `paramiko` — affected >=2.5.0 <3.4.0
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20231218163308-9d2ee975ef9f

## Details
### Summary

Terrapin is a prefix truncation attack targeting the SSH protocol. More precisely, Terrapin breaks the integrity of SSH's secure channel. By carefully adjusting the sequence numbers during the handshake, an attacker can remove an arbitrary amount of messages sent by the client or server at the beginning of the secure channel without the client or server noticing it.

### Mitigations

To mitigate this protocol vulnerability, OpenSSH suggested a so-called "strict kex" which alters the SSH handshake to ensure a Man-in-the-Middle attacker cannot introduce unauthenticated messages as well as convey sequence number manipulation across handshakes.

**Warning: To take effect, both the client and server must support this countermeasure.** 

As a stop-gap measure, peers may also (temporarily) disable the affected algorithms and use unaffected alternatives like AES-GCM instead until patches are available.

### Details

The SSH specifications of ChaCha20-Poly1305 (chacha20-poly1305@openssh.com) and Encrypt-then-MAC (*-etm@openssh.com MACs) are vulnerable against an arbitrary prefix truncation attack (a.k.a. Terrapin attack). This allows for an extension negotiation downgrade by stripping the SSH_MSG_EXT_INFO sent after the first message after SSH_MSG_NEWKEYS, downgrading security, and disabling attack countermeasures in some versions of OpenSSH. When targeting Encrypt-then-MAC, this attack requires the use of a CBC cipher to be practically exploitable due to the internal workings of the cipher mode. Additionally, this novel attack technique can be used to exploit previously unexploitable implementation flaws in a Man-in-the-Middle scenario.

The attack works by an attacker injecting an arbitrary number of SSH_MSG_IGNORE messages during the initial key exchange and consequently removing the same number of messages just after the initial key exchange has concluded. This is possible due to missing authentication of the excess SSH_MSG_IGNORE messages and the fact that the implicit sequence numbers used within the SSH protocol are only checked after the initial key exchange.

In the case of ChaCha20-Poly1305, the attack is guaranteed to work on every connection as this cipher does not maintain an internal state other than the message's sequence number. In the case of Encrypt-Then-MAC, practical exploitation requires the use of a CBC cipher; while theoretical integrity is broken for all ciphers when using this mode, message processing will fail at the application layer for CTR and stream ciphers.

For more details see [https://terrapin-attack.com](https://terrapin-attack.com). 

### Impact

This attack targets the specification of ChaCha20-Poly1305 (chacha20-poly1305@openssh.com) and Encrypt-then-MAC (*-etm@openssh.com), which are widely adopted by well-known SSH implementations and can be considered de-facto standard. These algorithms can be practically exploited; however, in the case of Encrypt-Then-MAC, we additionally require the use of a CBC cipher. As a consequence, this attack works against all well-behaving SSH implementations supporting either of those algorithms and can be used to downgrade (but not fully strip) connection security in case SSH extension negotiation (RFC8308) is supported. The attack may also enable attackers to exploit certain implementation flaws in a man-in-the-middle (MitM) scenario.

## References
- https://github.com/warp-tech/russh/security/advisories/GHSA-45x7-px36-x8w8
- https://nvd.nist.gov/vuln/detail/CVE-2023-48795
- https://github.com/ssh-mitm/ssh-mitm/issues/165
- https://github.com/hierynomus/sshj/issues/916
- https://github.com/janmojzis/tinyssh/issues/81
- https://github.com/cyd01/KiTTY/issues/520
- https://github.com/proftpd/proftpd/issues/456
- https://github.com/apache/mina-sshd/issues/445
- https://github.com/paramiko/paramiko/issues/2337#issuecomment-1887642773
- https://github.com/paramiko/paramiko/issues/2337
- https://github.com/PowerShell/Win32-OpenSSH/issues/2189
- https://github.com/mwiede/jsch/issues/457
- https://github.com/libssh2/libssh2/pull/1291
- https://github.com/NixOS/nixpkgs/pull/275249
- https://github.com/mwiede/jsch/pull/461
- https://github.com/TeraTermProject/teraterm/commit/7279fbd6ef4d0c8bdd6a90af4ada2899d786eec0
- https://github.com/mscdex/ssh2/commit/97b223f8891b96d6fc054df5ab1d5a1a545da2a3
- https://github.com/connectbot/sshlib/commit/5c8b534f6e97db7ac0e0e579331213aa25c173ab
- https://github.com/jtesta/ssh-audit/commit/8e972c5e94b460379fe0c7d20209c16df81538a5
- https://github.com/warp-tech/russh/commit/1aa340a7df1d5be1c0f4a9e247aade76dfdd2951
