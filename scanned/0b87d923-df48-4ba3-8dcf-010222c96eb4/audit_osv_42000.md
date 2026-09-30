# [H] exfat: bound uniname advance in exfat_find_dir_entry()

## Summary
Severity: High
Advisory: CVE-2026-64296
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64296
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: bound uniname advance in exfat_find_dir_entry()

In exfat_find_dir_entry(), each TYPE_EXTEND (file name) entry advances the
output pointer by a fixed amount while the loop guard only tracks the
accumulated name length:

	if (++order == 2)
		uniname = p_uniname->name;
	else
		uniname += EXFAT_FILE_NAME_LEN;
	len = exfat_extract_uni_name(ep, entry_uniname);
	name_len += len;
	unichar = *(uniname+len);
	*(uniname+len) = 0x0;

uniname grows by EXFAT_FILE_NAME_LEN (15) per name entry, but name_len
grows only by the actual extracted length, which is shorter when a name
fragment contains an early NUL.  The only guard is
`name_len >= MAX_NAME_LENGTH`, so a crafted directory with many short
name fragments lets uniname run far past the
p_uniname->name[MAX_NAME_LENGTH + 3] buffer while name_len stays small,
causing an out-of-bounds read and write at *(uniname+len).

The sibling extractor exfat_get_uniname_from_ext_entry() already stops
on a short fragment (the lockstep `len != EXFAT_FILE_NAME_LEN` guard
added in commit d42334578eba ("exfat: check if filename entries exceeds
max filename length")); exfat_find_dir_entry() never got the
equivalent.  Track the per-entry write offset as a count and reject a
fragment once the offset, or the offset plus the extracted length, would
exceed MAX_NAME_LENGTH, before forming the output pointer.

## References
- https://git.kernel.org/stable/c/33c0b96d7e1672be1de0053786637ea46fb81507
- https://git.kernel.org/stable/c/3a1230e7b043c62737b05a3e9275ca83a43ad20a
- https://git.kernel.org/stable/c/727bf7783a2936ffd55c628dddfd69343e511dcf
- https://git.kernel.org/stable/c/72a2589d82eb001c94b74bcfe6f9a599bd9bef60
- https://git.kernel.org/stable/c/c8e041c68c0bbb73aa62371ee63947bb6949d8b2
- https://git.kernel.org/stable/c/ce4736c1e6c4cfbf1ac409a8c328a0b69546c9a0
- https://git.kernel.org/stable/c/cf85180b8a015029ee147694eaf4e0b3537e9432
- https://git.kernel.org/stable/c/fae76a94b35ee8c0e2eb6f64caca01d75c6d34e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64296.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
