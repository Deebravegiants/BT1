# [H] ALPINE-CVE-2026-23554

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-23554
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-23554
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=4.17 <4.18.5-r5
- Alpine:v3.21: `xen` — affected >=4.17 <4.19.4-r2
- Alpine:v3.22: `xen` — affected >=4.17 <4.20.2-r2
- Alpine:v3.23: `xen` — affected >=4.17 <4.20.2-r2
- Alpine:v3.24: `xen` — affected >=4.17 <4.21.0-r3

## Details
The Intel EPT paging code uses an optimization to defer flushing of any cached
EPT state until the p2m lock is dropped, so that multiple modifications done
under the same locked region only issue a single flush.

Freeing of paging structures however is not deferred until the flushing is
done, and can result in freed pages transiently being present in cached state.
Such stale entries can point to memory ranges not owned by the guest, thus
allowing access to unintended memory regions.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-23554
