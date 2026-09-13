# [M] ALPINE-CVE-2020-29484

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29484
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29484
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
An issue was discovered in Xen through 4.14.x. When a Xenstore watch fires, the xenstore client that registered the watch will receive a Xenstore message containing the path of the modified Xenstore entry that triggered the watch, and the tag that was specified when registering the watch. Any communication with xenstored is done via Xenstore messages, consisting of a message header and the payload. The payload length is limited to 4096 bytes. Any request to xenstored resulting in a response with a payload longer than 4096 bytes will result in an error. When registering a watch, the payload length limit applies to the combined length of the watched path and the specified tag. Because watches for a specific path are also triggered for all nodes below that path, the payload of a watch event message can be longer than the payload needed to register the watch. A malicious guest that registers a watch using a very large tag (i.e., with a registration operation payload length close to the 4096 byte limit) can cause the generation of watch events with a payload length larger than 4096 bytes, by writing to Xenstore entries below the watched path. This will result in an error condition in xenstored. This error can result in a NULL pointer dereference, leading to a crash of xenstored. A malicious guest administrator can cause xenstored to crash, leading to a denial of service. Following a xenstored crash, domains may continue to run, but management operations will be impossible. Only C xenstored is affected, oxenstored is not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29484
