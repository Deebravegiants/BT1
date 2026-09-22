# [H] fs/ntfs3: Use variable length array instead of fixed size

## Summary
Severity: High
Advisory: CVE-2024-38623
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-38623
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Use variable length array instead of fixed size

Should fix smatch warning:
	ntfs_set_label() error: __builtin_memcpy() 'uni->name' too small (20 vs 256)

## References
- https://git.kernel.org/stable/c/1997cdc3e727526aa5d84b32f7cbb3f56459b7ef
- https://git.kernel.org/stable/c/1fe1c9dc21ee52920629d2d9b9bd84358931a8d1
- https://git.kernel.org/stable/c/3839a9b19a4b70eff6b6ad70446f639f7fd5a3d7
- https://git.kernel.org/stable/c/a2de301d90b782ac5d7a5fe32995caaee9ab3a0f
- https://git.kernel.org/stable/c/cceef44b34819c24bb6ed70dce5b524bd3e368d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38623.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38623
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
