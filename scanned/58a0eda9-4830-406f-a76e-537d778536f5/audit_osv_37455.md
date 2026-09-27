# [C] rxrpc: reject undecryptable rxkad response tickets

## Summary
Severity: Critical
Advisory: CVE-2026-31637
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31637
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: reject undecryptable rxkad response tickets

rxkad_decrypt_ticket() decrypts the RXKAD response ticket and then
parses the buffer as plaintext without checking whether
crypto_skcipher_decrypt() succeeded.

A malformed RESPONSE can therefore use a non-block-aligned ticket
length, make the decrypt operation fail, and still drive the ticket
parser with attacker-controlled bytes.

Check the decrypt result and abort the connection with RXKADBADTICKET
when ticket decryption fails.

## References
- https://git.kernel.org/stable/c/22f6258e7b31dba9bf88dce4e3ee7f0f20072e60
- https://git.kernel.org/stable/c/252157d939d179b5d767cb860ff8fa7f8723b67a
- https://git.kernel.org/stable/c/47073aab8a3a5a7b41c9bd37d2a3dcbeeccd6c8a
- https://git.kernel.org/stable/c/58fcd1b156152613ba00a064a129fb69507ddd7d
- https://git.kernel.org/stable/c/a149dcae23309df9de1c3b6b5d468610ef5ab7de
- https://git.kernel.org/stable/c/a75b3b361dd481d942c5f259a82d59718a41092c
- https://git.kernel.org/stable/c/b3a808cd0790b5075aaa2bc3588edf02cd71d352
- https://git.kernel.org/stable/c/fe4447cd95623b1cfacc15f280aab73a6d7340b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31637.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
