# [M] ext4: fix memory leak in parse_apply_sb_mount_options()

## Summary
Severity: Medium
Advisory: CVE-2022-49408
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49408
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix memory leak in parse_apply_sb_mount_options()

If processing the on-disk mount options fails after any memory was
allocated in the ext4_fs_context, e.g. s_qf_names, then this memory is
leaked.  Fix this by calling ext4_fc_free() instead of kfree() directly.

Reproducer:

    mkfs.ext4 -F /dev/vdc
    tune2fs /dev/vdc -E mount_opts=usrjquota=file
    echo clear > /sys/kernel/debug/kmemleak
    mount /dev/vdc /vdc
    echo scan > /sys/kernel/debug/kmemleak
    sleep 5
    echo scan > /sys/kernel/debug/kmemleak
    cat /sys/kernel/debug/kmemleak

## References
- https://git.kernel.org/stable/c/9ea3e6168948189cec31d0678d2b55b395f88491
- https://git.kernel.org/stable/c/c069db76ed7b681c69159f44be96d2137e9ca989
- https://git.kernel.org/stable/c/f92ded66e9d0aa20b883a2a5183973abc8f41815
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49408.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
