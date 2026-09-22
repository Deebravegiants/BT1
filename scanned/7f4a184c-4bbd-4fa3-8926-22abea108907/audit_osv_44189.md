# [C] libceph: fix multiple unsafe decodes in decode_locker()

## Summary
Severity: Critical
Advisory: CVE-2026-80561
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80561
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: fix multiple unsafe decodes in decode_locker()

decode_locker() in cls_lock_client.c contains three unsafe decode
operations that allow a malicious or compromised OSD to trigger
slab-out-of-bounds reads:

1. ceph_decode_copy() at the locker_id_t name field has no preceding
   bounds check. With p == end after ceph_start_decoding() accepts
   struct_len=0, this reads sizeof(ceph_entity_name) = 9 bytes past
   the validated buffer boundary.

2. *p += sizeof(struct ceph_timespec) after the locker_info_t header
   is an unchecked pointer advance. A malicious OSD can position p
   past end, causing all subsequent _safe checks to pass against a
   bogus boundary.

3. len = ceph_decode_32(p) has no preceding bounds check, and the
   immediately following *p += len is uncapped. A malicious OSD can
   send len=0xffffffff, advancing p gigabytes past end and escaping
   the decode window entirely.

Fix all three by replacing bare operations with their safe variants:
  ceph_decode_copy   -> ceph_decode_copy_safe
  *p += sizeof(...)  -> ceph_decode_skip_n
  ceph_decode_32(p)  -> ceph_decode_32_safe
  *p += len          -> ceph_decode_skip_n

A new label is added to return -EINVAL on any bounds violation.
-EINVAL is appropriate here: the data received from the OSD
is structurally malformed, which is an invalid argument to the decode
contract regardless of whether the caller or the wire is at fault.

Attacker model: a malicious or compromised OSD in a multi-tenant Ceph
deployment can trigger this against any kernel client that issues the
lock.get_info class method (e.g. during RBD exclusive lock acquisition)
without any further privileges beyond OSD session establishment.

[ idryomov: use ceph_decode_skip_string() to skip description, trim
  changelog ]

## References
- https://git.kernel.org/stable/c/1ed45c8d96498725eb54f740172f9068d8673906
- https://git.kernel.org/stable/c/3c3716dc06a34e4ca7f743f5fcfa07fbc5a11070
- https://git.kernel.org/stable/c/437b6551cfcc235eea1d735a874f9d421f555e17
- https://git.kernel.org/stable/c/51c8d238fe7236de627ab1a1433694552a904136
- https://git.kernel.org/stable/c/6265103e78f0ee7e2518de9cf938b94bee9700a0
- https://git.kernel.org/stable/c/d1bba38574d095f191557d397d9633f08cd966b1
- https://git.kernel.org/stable/c/dbfd83f722a78446ec18a476ef7a38e52240b50a
- https://git.kernel.org/stable/c/fa4aa86fff0c56799c2e3f51a88879053285f4a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80561.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80561
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
