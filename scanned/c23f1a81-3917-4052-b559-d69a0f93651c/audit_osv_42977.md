# [H] netfilter: nf_conntrack_sip: validate skb_dst() before accessing it

## Summary
Severity: High
Advisory: CVE-2026-72253
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72253
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_sip: validate skb_dst() before accessing it

tc ingress and openvswitch do not guarantee routing information to be
available. These subsystems use the conntrack helper infrastructure, and
the SIP helper relies on the skb_dst() to be present if
sip_external_media is set to 1 (which is disabled by default as a module
parameter).

This effectively disables the sip_external_media toggle for these
subsystems without resulting in a crash.

## References
- https://git.kernel.org/stable/c/09755dc62b026076b1d47f83489eb0547c8135e0
- https://git.kernel.org/stable/c/0aec339694a56e263d4b22475ff7211d40900830
- https://git.kernel.org/stable/c/7866116a040b3a23fb094e7d8f7ea3d61b3ac70b
- https://git.kernel.org/stable/c/b843a96252f672332837ea2ecb7c8db0acf68e20
- https://git.kernel.org/stable/c/c199ed687c00841daf60e9d131976958583a8c09
- https://git.kernel.org/stable/c/c5ef7228be04518d95591fc5369a9c554b19756d
- https://git.kernel.org/stable/c/e5e24a365a5e024efef63cc49abb345fbd4852c5
- https://git.kernel.org/stable/c/e64a48c50a1ff565a98c6a98d82b5b942868e76e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72253.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
