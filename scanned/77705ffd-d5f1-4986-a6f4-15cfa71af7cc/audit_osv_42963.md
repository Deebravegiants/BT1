# [H] batman-adv: ensure minimal ethernet header on TX

## Summary
Severity: High
Advisory: CVE-2026-72232
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72232
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: ensure minimal ethernet header on TX

As documented in commit 8bd67ebb50c0 ("net: bridge: xmit: make sure we have
at least eth header len bytes"), it is possible by for a local user with
eBPF TC hook access to attach a tc filter which truncates the packet and
redirects to an batadv interface. But the code assumes that at least
ETH_HLEN bytes are available and thus might read outside of the available
buffer.

The batadv_interface_tx() must therefore always check itself if enough data
is available for the ethernet header and don't rely on min_header_len.

## References
- https://git.kernel.org/stable/c/38cd10b0aeec755d89f78722a2b83f4088ff0cb0
- https://git.kernel.org/stable/c/49df66b7993c80b80c7eb9a84ba5b3410c8296a0
- https://git.kernel.org/stable/c/58799078afebd5115e052bf69ad6697f9759dd6f
- https://git.kernel.org/stable/c/6b4f521e01257387906f8b969ad3450d8208d4e2
- https://git.kernel.org/stable/c/811fea37620f2097955d95ce81cfdba03fd30f1b
- https://git.kernel.org/stable/c/9e16b6751a8206de0b865d99bb02771e6751d12d
- https://git.kernel.org/stable/c/dbeb4145d9778f922f459935da9a027750765a69
- https://git.kernel.org/stable/c/e6640923afee619d9fa82b07394dc9498e202304
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72232.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
