# [H] rbd: Reset positive result codes to zero in object map update path

## Summary
Severity: High
Advisory: CVE-2026-68131
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68131
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rbd: Reset positive result codes to zero in object map update path

In a reply message to an RBD request, a positive result code indicates
a data payload, which is not allowed for writes. While
rbd_osd_req_callback() already resets a positive result code for writes
to zero, rbd_object_map_callback() does not. This allows a corrupted
reply to an object map update to trigger the rbd_assert(*result < 0) in
__rbd_obj_handle_request(). This happens, because
rbd_object_map_callback() calls rbd_obj_handle_request() ->
__rbd_obj_handle_request() and passes this positive result code. From
__rbd_obj_handle_request(), rbd_obj_advance_write() is called, which
leaves the positive result code unchanged and returns true. Therefore,
the if(done && *result) branch is executed in __rbd_obj_handle_request()
and the assertion triggers.

This patch fixes the issue by adjusting the logic in the
rbd_object_map_callback() path. A positive result code for an object map
update is now reset to zero (similar to rbd_osd_req_callback()), and the
message is subsequently handled the same way as if the result code was
zero from the beginning. Additionally, a WARN_ON_ONCE() is added for
this case.

## References
- https://git.kernel.org/stable/c/14995c4250f04b58bf6fc00e0e973a2e1b3cfb9b
- https://git.kernel.org/stable/c/2419aa74081007dc4d14ff5640659052dfdfd69a
- https://git.kernel.org/stable/c/34f2a2f32af570dfcc532ad70c080629ee1c32b0
- https://git.kernel.org/stable/c/6f33d9d539fb94e5a17589c2dfe271ff9bb64904
- https://git.kernel.org/stable/c/a6c4250b81bd30beae94e1b7a4b26fa1193ad2e4
- https://git.kernel.org/stable/c/b1a61366933224b3ad80975c4d01ac2cc6931ecf
- https://git.kernel.org/stable/c/cf1167292f606deaddac35ec384eba48f08a68d2
- https://git.kernel.org/stable/c/da926959bf791441ba06a80571708c3d0d3cc08f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68131.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68131
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
