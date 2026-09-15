# [H] octeontx2-af: validate body pcifunc in rvu_mbox_handler_rep_event_notify

## Summary
Severity: High
Advisory: CVE-2026-63923
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63923
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.42, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: validate body pcifunc in rvu_mbox_handler_rep_event_notify

rvu_mbox_handler_rep_event_notify() in drivers/net/ethernet/marvell/
octeontx2/af/rvu_rep.c queues a sender-controlled REP_EVENT_NOTIFY
request body verbatim, and rvu_rep_up_notify() then forwards
event->pcifunc (the nested body field, distinct from the
AF-normalised header pcifunc) into rvu_get_pfvf(), rvu_get_pf() and
the AF->PF mailbox device index without any bounds check.

A VF attached to a PF that has been put into switchdev
representor mode reaches this path: the VF mailbox handler
otx2_pfvf_mbox_handler() forwards every message id including
MBOX_MSG_REP_EVENT_NOTIFY to AF without an allowlist, and the AF
dispatcher rewrites only msg->pcifunc, leaving struct
rep_event::pcifunc attacker-controlled.  The sibling
rvu_mbox_handler_esw_cfg() refuses requests whose header pcifunc
is not rvu->rep_pcifunc; this handler has no equivalent gate.

An out-of-range body pcifunc selects an &rvu->pf[]/&rvu->hwvf[]
element past the allocated array and, for RVU_EVENT_MAC_ADDR_CHANGE,
turns into a six-byte attacker-chosen OOB ether_addr_copy() target
inside the queued worker; KASAN reports a slab-out-of-bounds write
in rvu_rep_wq_handler.

Reject malformed requests at the handler entry by gating on
is_pf_func_valid(), which is already the canonical PF/VF range check
in this driver; expose it via rvu.h so callers in rvu_rep.c can use
it instead of open-coding the same range arithmetic.

## References
- https://git.kernel.org/stable/c/2156a29aecfffa2eb7c558255690084efbe9f3b0
- https://git.kernel.org/stable/c/4467fa514482bbce82f73788943c815f3d126ab3
- https://git.kernel.org/stable/c/68be0260e2a02ff9b18a8678d5f8d1715fa20138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63923.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63923
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
