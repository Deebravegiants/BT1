# [H] xfrm: hold dev ref until after transport_finish NF_HOOK

## Summary
Severity: High
Advisory: CVE-2026-31663
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31663
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.12.94, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: hold dev ref until after transport_finish NF_HOOK

After async crypto completes, xfrm_input_resume() calls dev_put()
immediately on re-entry before the skb reaches transport_finish.
The skb->dev pointer is then used inside NF_HOOK and its okfn,
which can race with device teardown.

Remove the dev_put from the async resumption entry and instead
drop the reference after the NF_HOOK call in transport_finish,
using a saved device pointer since NF_HOOK may consume the skb.
This covers NF_DROP, NF_QUEUE and NF_STOLEN paths that skip
the okfn.

For non-transport exits (decaps, gro, drop) and secondary
async return points, release the reference inline when
async is set.

## References
- https://git.kernel.org/stable/c/0f451b43c88bf2b9c038b414be580efee42e031b
- https://git.kernel.org/stable/c/1c428b03840094410c5fb6a5db30640486bbbfcb
- https://git.kernel.org/stable/c/4236c30b437b80f673b9e08c8fae38b8d471ac9e
- https://git.kernel.org/stable/c/5002beda5cac69d522dc54da0d5d463ed9c963d2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31663.json
- https://access.redhat.com/security/cve/CVE-2026-31663
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31663.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31663
- https://bugzilla.redhat.com/show_bug.cgi?id=2461462
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
