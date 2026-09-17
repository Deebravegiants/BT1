# [M] Rsync version 3.4.2 and prior contain a receiver-side out-of-bounds array read vulnerability in...

## Summary
Severity: Medium
Advisory: JLSEC-2026-631
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/JLSEC-2026-631
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.4+0

## Details
Rsync version 3.4.2 and prior contain a receiver-side out-of-bounds array read vulnerability in `recv_files()` in receiver.c that allows a malicious rsync server to crash the rsync client process. Attackers can exploit the vulnerability by setting `CF_INC_RECURSE` in compatibility flags and sending a specially crafted file list where the first sorted entry is not the leading dot directory, followed by a transfer record with ndx=0 and an iflag word without `ITEM_TRANSFER`, causing the receiver to read 8 bytes before the allocated pointer array and dereference an invalid pointer at an unmapped address, resulting in a deterministic SIGSEGV crash of the rsync client.

## References
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-28pw-r563-rxvm
- https://github.com/advisories/GHSA-jmf6-74r8-6c28
- https://nvd.nist.gov/vuln/detail/CVE-2026-43620
- https://www.vulncheck.com/advisories/rsync-out-of-bounds-array-read-via-recv-files
