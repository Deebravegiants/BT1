# [H] dm cache policy smq: fix missing locks in invalidating cache blocks

## Summary
Severity: High
Advisory: CVE-2026-53062
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53062
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm cache policy smq: fix missing locks in invalidating cache blocks

In passthrough mode, the policy invalidate_mapping operation is called
simultaneously from multiple workers, thus it should be protected by a
lock. Otherwise, we might end up with data races on the allocated blocks
counter, or even use-after-free issues with internal data structures
when doing concurrent writes.

Note that the existing FIXME in smq_invalidate_mapping() doesn't affect
passthrough mode since migration tasks don't exist there, but would need
attention if supporting fast device shrinking via suspend/resume without
target reloading.

Reproduce steps:

1. Create a cache device consisting of 1024 cache entries

dmsetup create cmeta --table "0 8192 linear /dev/sdc 0"
dmsetup create cdata --table "0 131072 linear /dev/sdc 8192"
dmsetup create corig --table "0 262144 linear /dev/sdc 262144"
dd if=/dev/zero of=/dev/mapper/cmeta bs=4k count=1 oflag=direct
dmsetup create cache --table "0 262144 cache /dev/mapper/cmeta \
/dev/mapper/cdata /dev/mapper/corig 128 2 metadata2 writethrough smq 0"

2. Populate the cache, and record the number of cached blocks

fio --name=populate --filename=/dev/mapper/cache --rw=randwrite --bs=4k \
--size=64m --direct=1
nr_cached=$(dmsetup status cache | awk '{split($7, a, "/"); print a[1]}')

3. Reload the cache into passthrough mode

dmsetup suspend cache
dmsetup reload cache --table "0 262144 cache /dev/mapper/cmeta \
/dev/mapper/cdata /dev/mapper/corig 128 2 metadata2 passthrough smq 0"
dmsetup resume cache

4. Write to the passthrough cache. By setting multiple jobs with I/O
   size equal to the cache block size, cache blocks are invalidated
   concurrently from different workers.

fio --filename=/dev/mapper/cache --name=test --rw=randwrite --bs=64k \
--direct=1 --numjobs=2 --randrepeat=0 --size=64m

5. Check if demoted matches cached block count. These numbers should
   match but may differ due to the data race.

nr_demoted=$(dmsetup status cache | awk '{print $12}')
echo "$nr_cached, $nr_demoted"

## References
- https://git.kernel.org/stable/c/1b2bec4a7dcf5f00b7a1cbeeec8997841d783513
- https://git.kernel.org/stable/c/2b62d0611c9af14a16bddf22df2612b4f40eb5a1
- https://git.kernel.org/stable/c/2d1f7b65f5deedd2e6b09fdc6ea27f8375f24b45
- https://git.kernel.org/stable/c/4991b5a08751e2e82488fb93ae08849b6aea10d9
- https://git.kernel.org/stable/c/93627a29d4b66d4a2def938dfb8610cc80ae454b
- https://git.kernel.org/stable/c/9a5fdfb9e57ec3a8ad2b8fce5e5ffa42d53b130e
- https://git.kernel.org/stable/c/ac5ee99443891bdb161f5539606a66a1b5e72542
- https://git.kernel.org/stable/c/c348ae47d8e65f06429fa41adce9ad986b696766
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53062.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
