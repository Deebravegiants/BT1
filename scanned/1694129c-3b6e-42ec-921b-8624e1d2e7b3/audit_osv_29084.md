# [H] media: mc: Fix graph walk in media_pipeline_start

## Summary
Severity: High
Advisory: CVE-2024-39481
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39481
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.94, >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mc: Fix graph walk in media_pipeline_start

The graph walk tries to follow all links, even if they are not between
pads. This causes a crash with, e.g. a MEDIA_LNK_FL_ANCILLARY_LINK link.

Fix this by allowing the walk to proceed only for MEDIA_LNK_FL_DATA_LINK
links.

## References
- https://git.kernel.org/stable/c/788fd0f11e45ae8d3a8ebbd3452a6e83f92db376
- https://git.kernel.org/stable/c/8a9d420149c477e7c97fbd6453704e4612bdd3fa
- https://git.kernel.org/stable/c/bee9440bc0b6b3b7432f7bfde28656262a3484a2
- https://git.kernel.org/stable/c/e80d9db99b7b6c697d8d952dfd25c3425cf61499
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39481.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
