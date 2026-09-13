# [M] CVE-2019-18786

## Summary
Severity: Medium
Advisory: CVE-2019-18786
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-06
Source: https://osv.dev/vulnerability/CVE-2019-18786
Type: osv

## Details
In the Linux kernel through 5.3.8, f->fmt.sdr.reserved is uninitialized in rcar_drif_g_fmt_sdr_cap in drivers/media/platform/rcar_drif.c, which could cause a memory disclosure problem.

## References
- https://usn.ubuntu.com/4287-2/
- https://usn.ubuntu.com/4284-1/
- https://usn.ubuntu.com/4285-1/
- https://usn.ubuntu.com/4287-1/
- https://patchwork.linuxtv.org/patch/59542/
