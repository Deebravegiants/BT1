# [H] netfilter: xt_IDLETIMER: reject rev0 reuse of ALARM timer labels

## Summary
Severity: High
Advisory: CVE-2026-23274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-23274
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_IDLETIMER: reject rev0 reuse of ALARM timer labels

IDLETIMER revision 0 rules reuse existing timers by label and always call
mod_timer() on timer->timer.

If the label was created first by revision 1 with XT_IDLETIMER_ALARM,
the object uses alarm timer semantics and timer->timer is never initialized.
Reusing that object from revision 0 causes mod_timer() on an uninitialized
timer_list, triggering debugobjects warnings and possible panic when
panic_on_warn=1.

Fix this by rejecting revision 0 rule insertion when an existing timer with
the same label is of ALARM type.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/144f88054ba0180467356f40895bd660b5dceeec
- https://git.kernel.org/stable/c/28c7cfaf0c0ab17cbd7754092116fd1af45271f9
- https://git.kernel.org/stable/c/329f0b9b48ee6ab59d1ab72fef55fe8c6463a6cf
- https://git.kernel.org/stable/c/32e937dc6e97f5ed3cdfe3fc0b2b19a05e23fa44
- https://git.kernel.org/stable/c/54080355999381fed4a26129579a5765bab87491
- https://git.kernel.org/stable/c/5e7ece24c5cb75a60402aad4d803c7898ea40aa9
- https://git.kernel.org/stable/c/f228b9ae2a7e84d1153616d8e71c4236cb1f1309
- https://git.kernel.org/stable/c/f5ef97c13165542480a6ffdbe6f09f40bbb7cbf1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23274.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
