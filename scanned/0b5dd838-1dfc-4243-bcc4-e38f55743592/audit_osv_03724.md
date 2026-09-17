# [M] ALPINE-CVE-2026-43620

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-43620
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43620
Type: osv

## Affected
- Alpine:v3.20: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.3-r0

## Details
Rsync version 3.4.2 and prior contain a receiver-side out-of-bounds array read vulnerability in recv_files() in receiver.c that allows a malicious rsync server to crash the rsync client process. Attackers can exploit the vulnerability by setting CF_INC_RECURSE in compatibility flags and sending a specially crafted file list where the first sorted entry is not the leading dot directory, followed by a transfer record with ndx=0 and an iflag word without ITEM_TRANSFER, causing the receiver to read 8 bytes before the allocated pointer array and dereference an invalid pointer at an unmapped address, resulting in a deterministic SIGSEGV crash of the rsync client.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43620
