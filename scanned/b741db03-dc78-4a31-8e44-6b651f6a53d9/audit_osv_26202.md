# [H] media: mtk-jpeg: Fix use after free bug due to error path handling in mtk_jpeg_dec_device_run

## Summary
Severity: High
Advisory: CVE-2023-52491
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52491
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mtk-jpeg: Fix use after free bug due to error path handling in mtk_jpeg_dec_device_run

In mtk_jpeg_probe, &jpeg->job_timeout_work is bound with
mtk_jpeg_job_timeout_work.

In mtk_jpeg_dec_device_run, if error happens in
mtk_jpeg_set_dec_dst, it will finally start the worker while
mark the job as finished by invoking v4l2_m2m_job_finish.

There are two methods to trigger the bug. If we remove the
module, it which will call mtk_jpeg_remove to make cleanup.
The possible sequence is as follows, which will cause a
use-after-free bug.

CPU0                  CPU1
mtk_jpeg_dec_...    |
  start worker	    |
                    |mtk_jpeg_job_timeout_work
mtk_jpeg_remove     |
  v4l2_m2m_release  |
    kfree(m2m_dev); |
                    |
                    | v4l2_m2m_get_curr_priv
                    |   m2m_dev->curr_ctx //use

If we close the file descriptor, which will call mtk_jpeg_release,
it will have a similar sequence.

Fix this bug by starting timeout worker only if started jpegdec worker
successfully. Then v4l2_m2m_job_finish will only be called in
either mtk_jpeg_job_timeout_work or mtk_jpeg_dec_device_run.

## References
- https://git.kernel.org/stable/c/1b1036c60a37a30caf6759a90fe5ecd06ec35590
- https://git.kernel.org/stable/c/206c857dd17d4d026de85866f1b5f0969f2a109e
- https://git.kernel.org/stable/c/43872f44eee6c6781fea1348b38885d8e78face9
- https://git.kernel.org/stable/c/6e2f37022f0fc0893da4d85a0500c9d547fffd4c
- https://git.kernel.org/stable/c/8254d54d00eb6cdb8367399c7f912eb8d354ecd7
- https://git.kernel.org/stable/c/9fec4db7fff54d9b0306a332bab31eac47eeb5f6
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52491.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52491
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
