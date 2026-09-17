# [H] ext4: drop ppath from ext4_ext_replay_update_ex() to avoid double-free

## Summary
Severity: High
Advisory: CVE-2024-49983
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49983
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: drop ppath from ext4_ext_replay_update_ex() to avoid double-free

When calling ext4_force_split_extent_at() in ext4_ext_replay_update_ex(),
the 'ppath' is updated but it is the 'path' that is freed, thus potentially
triggering a double-free in the following process:

ext4_ext_replay_update_ex
  ppath = path
  ext4_force_split_extent_at(&ppath)
    ext4_split_extent_at
      ext4_ext_insert_extent
        ext4_ext_create_new_leaf
          ext4_ext_grow_indepth
            ext4_find_extent
              if (depth > path[0].p_maxdepth)
                kfree(path)                 ---> path First freed
                *orig_path = path = NULL    ---> null ppath
  kfree(path)                               ---> path double-free !!!

So drop the unnecessary ppath and use path directly to avoid this problem.
And use ext4_find_extent() directly to update path, avoiding unnecessary
memory allocation and freeing. Also, propagate the error returned by
ext4_find_extent() instead of using strange error codes.

## References
- https://git.kernel.org/stable/c/1b558006d98b7b0b730027be0ee98973dd10ee0d
- https://git.kernel.org/stable/c/3ff710662e8d86a63a39b334e9ca0cb10e5c14b0
- https://git.kernel.org/stable/c/5c0f4cc84d3a601c99bc5e6e6eb1cbda542cce95
- https://git.kernel.org/stable/c/6367d3f04c69e2b8770b8137bd800e0784b0abbc
- https://git.kernel.org/stable/c/63adc9016917e6970fb0104ee5fd6770f02b2d80
- https://git.kernel.org/stable/c/8c26d9e53e5fbacda0732a577e97c5a5b7882aaf
- https://git.kernel.org/stable/c/a34bed978364114390162c27e50fca50791c568d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49983.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49983
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
