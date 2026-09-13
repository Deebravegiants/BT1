# [H] ALPINE-CVE-2026-42492

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42492
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42492
Type: osv

## Affected
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
Xenstore, to have an up-to-date picture of the entire system, wants to
know of domains appearing and disappearing.  To make this more robust, a
new XEN_DOMCTL_get_domain_state was introduced.  The management of the
bitmap underlying that operation is tied into the binding of the
VIRQ_DOM_EXC virtual IRQ.  Unfortunately an error path there would tear
down the bitmap even in cases when it wasn't set up.  Unprivileged domains
can trigger that error path.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42492
