# [H] media: mediatek: vcodec: Fix potential array out-of-bounds in decoder queue_setup

## Summary
Severity: High
Advisory: CVE-2023-53748
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2023-53748
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mediatek: vcodec: Fix potential array out-of-bounds in decoder queue_setup

variable *nplanes is provided by user via system call argument. The
possible value of q_data->fmt->num_planes is 1-3, while the value
of *nplanes can be 1-8. The array access by index i can cause array
out-of-bounds.

Fix this bug by checking *nplanes against the array size.

## References
- https://git.kernel.org/stable/c/48e4e06e2c5fe1fda283d499f91492eda2248bb9
- https://git.kernel.org/stable/c/8fbcf730cb89c3647f3365226fe7014118fa93c7
- https://git.kernel.org/stable/c/b8e19bf3b4aebd855be01b64674187dcf6d1db51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53748.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
