# [C] ntfs: not change 0-byte $DATA attribute to non-resident

## Summary
Severity: Critical
Advisory: CVE-2026-72207
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72207
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: not change 0-byte $DATA attribute to non-resident

When ntfs_resident_attr_resize() cannot grow a resident attribute in
place, it retries after converting other resident attributes to
non-resident to free space in the MFT recrord.

Do not select zero-length resident $DATA attributes for this conversion.
fsck treats 0-byte non-resident $DATA attribute as corruptions.

## References
- https://git.kernel.org/stable/c/0aad21570197973af4a1b25b3fb8ed3aeb9e7670
- https://git.kernel.org/stable/c/ceb49c37250125d418410988f2376ed4d57a6706
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72207.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72207
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
