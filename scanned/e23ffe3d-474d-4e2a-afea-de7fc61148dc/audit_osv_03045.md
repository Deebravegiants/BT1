# [M] ALPINE-CVE-2024-31497

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-31497
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-31497
Type: osv

## Affected
- Alpine:v3.16: `putty` — affected >=0.68 <0.81-r0
- Alpine:v3.17: `putty` — affected >=0.68 <0.81-r0
- Alpine:v3.18: `putty` — affected >=0.68 <0.81-r0
- Alpine:v3.19: `putty` — affected >=0.68 <0.81-r0

## Details
In PuTTY 0.68 through 0.80 before 0.81, biased ECDSA nonce generation allows an attacker to recover a user's NIST P-521 secret key via a quick attack in approximately 60 signatures. This is especially important in a scenario where an adversary is able to read messages signed by PuTTY or Pageant. The required set of signed messages may be publicly readable because they are stored in a public Git service that supports use of SSH for commit signing, and the signatures were made by Pageant through an agent-forwarding mechanism. In other words, an adversary may already have enough signature information to compromise a victim's private key, even if there is no further use of vulnerable PuTTY versions. After a key compromise, an adversary may be able to conduct supply-chain attacks on software maintained in Git. A second, independent scenario is that the adversary is an operator of an SSH server to which the victim authenticates (for remote login or file copy), even though this server is not fully trusted by the victim, and the victim uses the same private key for SSH connections to other services operated by other entities. Here, the rogue server operator (who would otherwise have no way to determine the victim's private key) can derive the victim's private key, and then use it for unauthorized access to those other services. If the other services include Git services, then again it may be possible to conduct supply-chain attacks on software maintained in Git. This also affects, for example, FileZilla before 3.67.0, WinSCP before 6.3.3, TortoiseGit before 2.15.0.1, and TortoiseSVN through 1.14.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-31497
