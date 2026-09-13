# [M] Rsync < 3.4.3 Out-of-Bounds Array Read via recv_files()

## Summary
Severity: Medium
Advisory: CVE-2026-43620
Aliases: GHSA-28pw-r563-rxvm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-43620
Type: osv

## Details
Rsync version 3.4.2 and prior contain a receiver-side out-of-bounds array read vulnerability in recv_files() in receiver.c that allows a malicious rsync server to crash the rsync client process. Attackers can exploit the vulnerability by setting CF_INC_RECURSE in compatibility flags and sending a specially crafted file list where the first sorted entry is not the leading dot directory, followed by a transfer record with ndx=0 and an iflag word without ITEM_TRANSFER, causing the receiver to read 8 bytes before the allocated pointer array and dereference an invalid pointer at an unmapped address, resulting in a deterministic SIGSEGV crash of the rsync client.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43620.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-28pw-r563-rxvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-43620
- https://www.vulncheck.com/advisories/rsync-out-of-bounds-array-read-via-recv-files
- https://github.com/RsyncProject/rsync
