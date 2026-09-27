# [M] netfs/fscache: Add a memory barrier for FSCACHE_VOLUME_CREATING

## Summary
Severity: Medium
Advisory: CVE-2024-56755
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56755
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs/fscache: Add a memory barrier for FSCACHE_VOLUME_CREATING

In fscache_create_volume(), there is a missing memory barrier between the
bit-clearing operation and the wake-up operation. This may cause a
situation where, after a wake-up, the bit-clearing operation hasn't been
detected yet, leading to an indefinite wait. The triggering process is as
follows:

  [cookie1]                [cookie2]                  [volume_work]
fscache_perform_lookup
  fscache_create_volume
                        fscache_perform_lookup
                          fscache_create_volume
			                        fscache_create_volume_work
                                                  cachefiles_acquire_volume
                                                  clear_and_wake_up_bit
    test_and_set_bit
                            test_and_set_bit
                              goto maybe_wait
      goto no_wait

In the above process, cookie1 and cookie2 has the same volume. When cookie1
enters the -no_wait- process, it will clear the bit and wake up the waiting
process. If a barrier is missing, it may cause cookie2 to remain in the
-wait- process indefinitely.

In commit 3288666c7256 ("fscache: Use clear_and_wake_up_bit() in
fscache_create_volume_work()"), barriers were added to similar operations
in fscache_create_volume_work(), but fscache_create_volume() was missed.

By combining the clear and wake operations into clear_and_wake_up_bit() to
fix this issue.

## References
- https://git.kernel.org/stable/c/22f9400a6f3560629478e0a64247b8fcc811a24d
- https://git.kernel.org/stable/c/539fabba965e119b98066fc6ba5257b5eaf4eda2
- https://git.kernel.org/stable/c/8beb682cc9a0798a280bbb95e3e41617237090b2
- https://git.kernel.org/stable/c/8cc1df3113cb71a0df2c46dd5b102c9e11c8a8c6
- https://git.kernel.org/stable/c/ddab02607eed9e415dc62fde421d4329e5345315
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56755.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
