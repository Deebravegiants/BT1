# [H] tls: don't leave a full plaintext sk_msg ring unpushed

## Summary
Severity: High
Advisory: CVE-2026-74610
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74610
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: don't leave a full plaintext sk_msg ring unpushed

When the copy path in tls_sw_sendmsg_locked() adds the fragment that fills
the plaintext sk_msg ring, it does not set full_record, so the record is
left full and unpushed.  A later splice() then adds to an already full
ring: sk_msg_page_add() has no fullness check of its own, so sg.end wraps
onto sg.start and the ring appears empty.  Fragments added after that
overwrite live entries, and sg.size no longer matches what is reachable
between sg.start and sg.end, so pushing the record runs the scatterwalk off
the end of the scatterlist.

An unprivileged user can trigger this on a loopback TCP socket with the
"tls" ULP attached:

  BUG: kernel NULL pointer dereference, address: 0000000000000008
  RIP: 0010:memcpy_from_scatterwalk+0x32/0xc0
  Call Trace:
   skcipher_walk_next+0x1d1/0x2c0
   gcm_encrypt_aesni_avx+0x1e9/0x220
   bpf_exec_tx_verdict+0x3bb/0x860
   tls_sw_sendmsg+0xa1a/0xca0
   __sys_sendto+0x1da/0x1f0

Set full_record in the copy path when the ring becomes full, and push a
record that is already full on entry to the sendmsg loop.

## References
- https://git.kernel.org/stable/c/3c5f8f2aa57c647b83add4896aab64aac5fdedad
- https://git.kernel.org/stable/c/3fc5044796dd87b8d68be4207046f5ce2748174c
- https://git.kernel.org/stable/c/7bca91d63341274e857f4aeaad54d229405e93dc
- https://git.kernel.org/stable/c/aa8b14647721b5a4958712b35cf43e3125d47753
- https://git.kernel.org/stable/c/f634289a0b557a197c5f37284b623cefedfe73d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74610.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74610
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
