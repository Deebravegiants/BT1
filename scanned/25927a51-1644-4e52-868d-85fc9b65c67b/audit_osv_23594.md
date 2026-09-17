# [M] net/sched: act_ct: fix ref leak when switching zones

## Summary
Severity: Medium
Advisory: CVE-2022-49183
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49183
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.258, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_ct: fix ref leak when switching zones

When switching zones or network namespaces without doing a ct clear in
between, it is now leaking a reference to the old ct entry. That's
because tcf_ct_skb_nfct_cached() returns false and
tcf_ct_flow_table_lookup() may simply overwrite it.

The fix is to, as the ct entry is not reusable, free it already at
tcf_ct_skb_nfct_cached().

## References
- https://git.kernel.org/stable/c/4bb42d73def9411e5cad885b9811987d72431df1
- https://git.kernel.org/stable/c/9222a08be539cbb7a8e0d46cbc7ab9e4db273eb8
- https://git.kernel.org/stable/c/b24793a37d91aacad7cb9893b226a7924a89636a
- https://git.kernel.org/stable/c/bcb74e132a76ce0502bb33d5b65533a4ed72d159
- https://git.kernel.org/stable/c/bcbf4e5c3b5b373cd61528392dd1ec8e9c0fd33d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49183.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49183
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
