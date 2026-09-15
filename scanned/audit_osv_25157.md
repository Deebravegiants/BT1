# [M] CVE-2023-3161

## Summary
Severity: Medium
Advisory: CVE-2023-3161
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-12
Source: https://osv.dev/vulnerability/CVE-2023-3161
Type: osv

## Details
A flaw was found in the Framebuffer Console (fbcon) in the Linux Kernel. When providing font->width and font->height greater than 32 to fbcon_set_font, since there are no checks in place, a shift-out-of-bounds occurs leading to undefined behavior and possible denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3161.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3161
- https://bugzilla.redhat.com/show_bug.cgi?id=2213485
- https://github.com/torvalds/linux/commit/2b09d5d364986f724f17001ccfe4126b9b43a0be
