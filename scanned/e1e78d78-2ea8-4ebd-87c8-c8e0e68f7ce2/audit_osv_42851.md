# [C] drbd: reject data replies with an out-of-range payload size

## Summary
Severity: Critical
Advisory: CVE-2026-72014
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72014
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drbd: reject data replies with an out-of-range payload size

recv_dless_read() receives a P_DATA_REPLY from a peer into the bio of an
outstanding read request. The peer-supplied payload length reaches it as
the signed int data_size, and two peer-controlled inputs can make it
negative. With a negotiated data-integrity-alg the digest length is
subtracted first, so a reply whose payload is smaller than the digest
underflows data_size. With no integrity algorithm (the default) data_size
is assigned from the unsigned h95/h100 wire length and drbdd() never
bounds it for a payload-carrying command, so a length above INT_MAX casts
it negative; this path needs no non-default feature. The bio receive loop
then computes expect = min_t(int, data_size, bv_len), which is negative,
and drbd_recv_all_warn(mapped, expect) receives with a size_t of SIZE_MAX
into the first mapped page.

The sibling receive path read_in_block() is not affected: it uses an
unsigned size and rejects it against DRBD_MAX_BIO_SIZE before receiving.
Reject a data reply whose size is negative after the optional digest
subtraction, covering both triggers.

Impact: a malicious or man-in-the-middle DRBD peer copies attacker-chosen
bytes past a bio page in the receiver, corrupting kernel memory. A node
that reads from its peer (a diskless node, or read-balancing to the peer)
is exposed in the default configuration; data-integrity-alg is not
required.

## References
- https://git.kernel.org/stable/c/38cc4867540ae8beedfe41a1a1a6ed37052c77d6
- https://git.kernel.org/stable/c/5f59a8142000f0b8f75c432209ead73c424a745d
- https://git.kernel.org/stable/c/648d4317326e6aa3f8c05cbf0fd14cc2eba6ca99
- https://git.kernel.org/stable/c/741a682535deffe9ab7e5c89caf83571efbc9dd9
- https://git.kernel.org/stable/c/bca33f5442c3094511719d9db792ce3165d87e76
- https://git.kernel.org/stable/c/bd910a7660d280595ef94cb6d193951d855d330f
- https://git.kernel.org/stable/c/f14e87d7b166490bceb9603b39310e51595d05b9
- https://git.kernel.org/stable/c/f16866c62656865854106b79bcf6e4ca97a51a92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72014.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72014
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
