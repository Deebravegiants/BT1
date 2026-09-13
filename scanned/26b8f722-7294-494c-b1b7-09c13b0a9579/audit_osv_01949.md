# [M] ALPINE-CVE-2020-29483

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29483
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29483
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.12: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.13: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.14.1-r0

## Details
An issue was discovered in Xen through 4.14.x. Xenstored and guests communicate via a shared memory page using a specific protocol. When a guest violates this protocol, xenstored will drop the connection to that guest. Unfortunately, this is done by just removing the guest from xenstored's internal management, resulting in the same actions as if the guest had been destroyed, including sending an @releaseDomain event. @releaseDomain events do not say that the guest has been removed. All watchers of this event must look at the states of all guests to find the guest that has been removed. When an @releaseDomain is generated due to a domain xenstored protocol violation, because the guest is still running, the watchers will not react. Later, when the guest is actually destroyed, xenstored will no longer have it stored in its internal data base, so no further @releaseDomain event will be sent. This can lead to a zombie domain; memory mappings of that guest's memory will not be removed, due to the missing event. This zombie domain will be cleaned up only after another domain is destroyed, as that will trigger another @releaseDomain event. If the device model of the guest that violated the Xenstore protocol is running in a stub-domain, a use-after-free case could happen in xenstored, after having removed the guest from its internal data base, possibly resulting in a crash of xenstored. A malicious guest can block resources of the host for a period after its own death. Guests with a stub domain device model can eventually crash xenstored, resulting in a more serious denial of service (the prevention of any further domain management operations). Only the C variant of Xenstore is affected; the Ocaml variant is not affected. Only HVM guests with a stubdom device model can cause a serious DoS.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29483
