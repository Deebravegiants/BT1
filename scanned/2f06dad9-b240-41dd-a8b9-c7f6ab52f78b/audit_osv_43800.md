# [C] sctp: validate cookie AUTH state before use

## Summary
Severity: Critical
Advisory: CVE-2026-74752
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74752
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate cookie AUTH state before use

When cookie authentication is disabled, COOKIE_ECHO restores fixed-size
AUTH fields directly from peer-controlled cookie bytes.  A forged RANDOM
length, HMAC list, or CHUNKS list can then reach association consumers
with lengths or identifiers that were never validated against the local
backing arrays.

A forged RANDOM length can cause out-of-bounds reads during key-vector
construction.  A forged HMAC identifier also caused a 32-byte write past
a zero-length AUTH chunk, providing a primitive for a local privilege
escalation chain.

Validate the cookie's RANDOM, HMACS, and CHUNKS parameters at the cookie
trust boundary before copying them into the association.  Reject invalid
types, malformed lengths, unsupported HMAC identifiers, HMAC lists
without SHA1, and forbidden chunk ids.

## References
- https://git.kernel.org/stable/c/3dbb44d88b1e94dd31fe43588af7437b34b44d56
- https://git.kernel.org/stable/c/88619b117be1daf633ce32210570ce35a0bd1c98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74752.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74752
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
