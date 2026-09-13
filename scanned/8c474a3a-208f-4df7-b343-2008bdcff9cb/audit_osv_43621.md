# [H] binfmt_misc: reject a flag character as the field delimiter

## Summary
Severity: High
Advisory: CVE-2026-74485
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74485
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

binfmt_misc: reject a flag character as the field delimiter

The registration string starts with a user chosen delimiter that
separates the individual fields. So that the field parsers terminate
even on a truncated string create_entry() pads the buffer with that
same delimiter:

	memset(buf + count, del, 8);

Most fields are scanned for the delimiter with strchr()/scanarg() and
happily stop on the padding. The flags field is different: instead of
scanning for the delimiter check_special_flags() consumes the flag
characters 'P', 'O', 'C' and 'F' and stops at the first byte that is
none of them, relying on the trailing delimiter to end the scan.

If the delimiter is itself a flag character the padding no longer acts
as a terminator. The scan swallows all eight padding bytes and keeps
reading past the end of the allocation until it hits a byte that is
not a flag character. For example registering

	PaPEPPxPPiP

with 'P' as the delimiter (name "a", type extension, magic "x",
interpreter "i", empty flags) leaves the flag scan running off the end
of the buffer. The registration is rejected in the end because the
parser does not stop exactly at buf + count, but only after the out of
bounds read has already happened. With an unlucky allocation layout the
scan can walk into an unmapped page; under KASAN it is reported as a
slab out of bounds read. binfmt_misc mounts are available to
unprivileged users in a user namespace so the read is reachable without
privileges.

Reject a delimiter that is one of the flag characters up front. Such a
registration was always rejected anyway, only after the out of bounds
read, so no valid registration string changes meaning.

## References
- https://git.kernel.org/stable/c/1819f82dee766c58295ecaacdac02cdf6837d7a4
- https://git.kernel.org/stable/c/1853e95c9bfe69ef1dd862b3f551e68f4a1b76cc
- https://git.kernel.org/stable/c/840bb9c49c3e75fb32b593d67ab32f6b77122262
- https://git.kernel.org/stable/c/8e85d50ba1117fd446bf9a250bd8a97d48384bdc
- https://git.kernel.org/stable/c/96bd5d4fea2970b9b08265293ca7a10b9b27c0fd
- https://git.kernel.org/stable/c/9970e094e5d60f0d66914bf9a97d1ef19107ebf5
- https://git.kernel.org/stable/c/9a2d87db3898b5993b64fd258d0334e0eba9ee0d
- https://git.kernel.org/stable/c/b29e3c1f375c1296362d219ff38bceddf2d2a88a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74485.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74485
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
