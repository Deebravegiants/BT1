# [H] bpf: sockmap: fix tail fragment offset in bpf_msg_push_data

## Summary
Severity: High
Advisory: CVE-2026-63926
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63926
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: sockmap: fix tail fragment offset in bpf_msg_push_data

When bpf_msg_push_data() inserts data in the middle of a scatterlist
entry, it splits the original entry into a left fragment and a right
fragment.

The right fragment offset is page-local, but the code advances it with
`start`, which is the message-global insertion point. For inserts into a
non-first SG entry, this over-advances the offset and leaves the split
layout inconsistent.

Advance the right fragment offset by the fragment-local delta,
`start - offset`, which matches the length removed from the front of the
original entry.

## References
- https://git.kernel.org/stable/c/3075c21d2d76c0067f4a382765b43d6cc10470f1
- https://git.kernel.org/stable/c/5e19028667963fb371ebb00cecc2a473ef92056b
- https://git.kernel.org/stable/c/63f64a510c7917658ddf4d073ece73914ee25346
- https://git.kernel.org/stable/c/96b72672ce849a1402730238e64d9b20bf06a96d
- https://git.kernel.org/stable/c/aeb95146848d12206e1b2cfacd4f40e21ce81d94
- https://git.kernel.org/stable/c/d81b323af2dcee47573907ccb89c0df9b45cb2e2
- https://git.kernel.org/stable/c/f14609d8146707452e0822f3c8154674ce677251
- https://git.kernel.org/stable/c/f72eed9b84fb771019a955908132410a9ba9ea3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63926.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
