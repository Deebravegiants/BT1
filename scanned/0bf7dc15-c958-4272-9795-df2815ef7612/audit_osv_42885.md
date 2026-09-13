# [H] dm: avoid leaking the caller's thread keyring via the table device file

## Summary
Severity: High
Advisory: CVE-2026-72103
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72103
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: avoid leaking the caller's thread keyring via the table device file

The refactoring in commit a28d893eb327 ("md: port block device access to file")
accidentally causes the caller's thread keyring to be kept alive long
beyond the caller's lifetime.

As a result, "cryptsetup luksSuspend" silently fails to wipe the
LUKS volume key from memory.

In detail: "cryptsetup luksOpen" uses its supposedly ephemeral thread
keyring to pass the volume key to the kernel. dm-crypt's
crypt_set_keyring_key() copies the key material into its own
crypt_config structure and then drops its own reference to the key in
the keyring with key_put().

With this fix, restoring pre-v6.9 behavior, the copy in the thread
keyring is then promptly garbage collected, such that exactly one copy
of the volume key remains. This single copy is correctly wiped from
memory on "cryptsetup luksSuspend".

Without this fix, the thread keyring and the volume key in it remains.
This second copy is only freed on "luksClose". "luksSuspend" neither
knows about this copy nor has any way to remove it, so the key remains
recoverable from RAM after a suspend that is documented to have wiped it.

This fix should not introduce new security problems, as the code is
anyway gated by CAP_SYS_ADMIN. The device-mapper core, not the calling
task, is the legitimate owner of this long-lived file.

## References
- https://git.kernel.org/stable/c/8ced1d242c34e342defcccdb00663354f212aae6
- https://git.kernel.org/stable/c/981ccd97f7153d310dfa92a534525bbaf46752c2
- https://git.kernel.org/stable/c/d3eb8451d529ea452740d1a2bc395a1d20c48133
- https://git.kernel.org/stable/c/f00105be6a593920e9bc7949a069d4a116888851
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72103.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72103
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
