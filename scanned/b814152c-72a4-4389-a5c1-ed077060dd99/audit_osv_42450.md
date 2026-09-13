# [C] ceph: fix pre-auth out-of-bounds read on snaptrace in ceph_handle_caps()

## Summary
Severity: Critical
Advisory: CVE-2026-68160
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68160
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix pre-auth out-of-bounds read on snaptrace in ceph_handle_caps()

ceph_handle_caps() reads snap_trace_len from the wire-format
ceph_mds_caps header and uses it unconditionally to build a fake
end pointer (snaptrace + snaptrace_len) that is later handed to
ceph_update_snap_trace() in the CEPH_CAP_OP_IMPORT case:

    snaptrace     = h + 1;
    snaptrace_len = le32_to_cpu(h->snap_trace_len);
    p             = snaptrace + snaptrace_len;
    ...
    case CEPH_CAP_OP_IMPORT:
        if (snaptrace_len) {
            ...
            if (ceph_update_snap_trace(mdsc, snaptrace,
                                       snaptrace + snaptrace_len,
                                       false, &realm)) { ... }

ceph_update_snap_trace() then decodes a struct ceph_mds_snap_realm
from snaptrace using ceph_decode_need(&p, e, sizeof(*ri), bad)
with the attacker-supplied fake end e == snaptrace + snaptrace_len.
With snaptrace_len == 0xFFFFFFFF the bound check is trivially
satisfied, ri = p reads sizeof(struct ceph_mds_snap_realm) past
the legitimate msg->front buffer, and ri->num_snaps /
ri->num_prior_parent_snaps then drive further out-of-bounds
reads of the encoded snap arrays.

The eleven msg_version >= 2 .. msg_version >= 12 decoder blocks
above the op switch each catch this OOB through their
ceph_decode_*_safe() / ceph_decode_need() helpers, but they sit
behind a hdr.version-gated if, so a malicious or compromised
MDS that sets msg->hdr.version = 1 reaches the IMPORT path with
no version-gated decoder having validated snap_trace_len. The
shape has been present since ceph_handle_caps() was introduced.

Validate snap_trace_len against the message front buffer before
consuming it, using the canonical ceph_decode_need() / ceph_has_room()
helper.  The helper bounds the length with subtraction (n <= end - p,
guarded by end >= p) rather than pointer addition, so it is wrap-safe
for the attacker-controlled u32 length on 32-bit builds where
p + snap_trace_len could overflow the address space.  This matches the
rest of the ceph decode path (e.g. the pool_ns_len check a few lines
below), and the existing goto bad cleanup already covers this exit
path.

## References
- https://git.kernel.org/stable/c/03b417afce19ee6b6e61f1bbbbebac924c9f36d1
- https://git.kernel.org/stable/c/0c011137194036424e974677e0f1592e22a33d8c
- https://git.kernel.org/stable/c/4dbc71bcaf9a30abf3920a4e2cc4ed33bba78c02
- https://git.kernel.org/stable/c/71893c342a26bcff92eaab0b2b75d64aed19308a
- https://git.kernel.org/stable/c/9081c71796724ffe96cba253f68fbe42363c5295
- https://git.kernel.org/stable/c/a4228b93706fb74a484e6ffb271c1cc2af3a2ddb
- https://git.kernel.org/stable/c/cc93f68a31c9b831abf2db8647b5f5b10329d793
- https://git.kernel.org/stable/c/f913192fc782288e060dafc329b2346934be34cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68160.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68160
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
