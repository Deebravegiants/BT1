# [C] libceph: fix two unsafe bare decodes in decode_lockers()

## Summary
Severity: Critical
Advisory: CVE-2026-68082
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-08
Source: https://osv.dev/vulnerability/CVE-2026-68082
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: fix two unsafe bare decodes in decode_lockers()

decode_lockers() in cls_lock_client.c contains two bare decode operations
that allow a malicious or compromised OSD to trigger slab-out-of-bounds
reads:

1. ceph_decode_32(p) at the num_lockers field has no preceding bounds
   check. ceph_start_decoding() accepts struct_len=0 as valid -- the
   internal ceph_decode_need(p, end, 0, bad) always passes -- so when an
   OSD sends struct_len=0, ceph_start_decoding() returns success with
   p == end. The immediately following bare ceph_decode_32(p) then reads
   4 bytes past the validated buffer boundary. The garbage value is
   passed directly to kzalloc_objs() as the locker count.

   The sibling function decode_watchers() in osd_client.c already uses
   ceph_decode_32_safe() after its own ceph_start_decoding() call.
   decode_lockers() was the only site using the bare variant.

2. ceph_decode_8(p) after the decode_locker() loop has no preceding
   bounds check. If an OSD crafts num_lockers such that the loop
   advances p exactly to end, the subsequent bare ceph_decode_8(p) reads
   one byte past the validated buffer boundary. The result is passed
   directly into *type, which is used as a lock type discriminator by
   callers, giving an OSD-controlled one-byte OOB read with direct
   influence over the lock type field.

Fix both by replacing bare operations with their safe variants:
  ceph_decode_32(p) -> ceph_decode_32_safe(p, end, *num_lockers,
                                           err_inval)
  ceph_decode_8(p)  -> ceph_decode_8_safe(p, end, *type,
                                          err_free_lockers)

The goto targets differ intentionally:
  err_inval: is a new label returning -EINVAL directly. It is used for
  the pre-allocation failure path where *lockers is not yet allocated
  and must not be passed to ceph_free_lockers().

  err_free_lockers: is the existing label. It is used for the
  post-allocation failure path where *lockers is allocated and must
  be freed.

ret is set to -EINVAL before ceph_decode_8_safe() so that
err_free_lockers returns the correct error code on bounds violation.
Without this, err_free_lockers would return a stale ret value (0 from
the successful decode_locker() loop), silently swallowing the error.

-EINVAL is correct for both failure paths. The data received from the
OSD is structurally malformed. -ENOMEM would misrepresent the failure
class to callers and to stable@ backporters triaging error paths.

Attacker model: a malicious or compromised OSD in a multi-tenant Ceph
deployment can trigger this against any kernel client that issues the
lock.get_info class method (e.g. during RBD exclusive lock acquisition).

[ idryomov: trim changelog, formatting ]

## References
- https://git.kernel.org/stable/c/001835c599899ef1bd3506a815110a6374451554
- https://git.kernel.org/stable/c/02430f6f729b297e803d0605871f0a670b4eafd6
- https://git.kernel.org/stable/c/57ba829804fe6d34bbac3b826c4b15c1caa54862
- https://git.kernel.org/stable/c/7c422364acd93d7da1dfc27d6b54635a269653a1
- https://git.kernel.org/stable/c/89df5d71f83f8e2781286798fd8ae5e42cf5f1a7
- https://git.kernel.org/stable/c/a109a556115271ca7896dcda7b4b7e45e156c227
- https://git.kernel.org/stable/c/a54be593d0b749161b08a1e56189b2cb9114267a
- https://git.kernel.org/stable/c/c8ade01170a27d8ede0d761c255268af81e417f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68082.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68082
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
