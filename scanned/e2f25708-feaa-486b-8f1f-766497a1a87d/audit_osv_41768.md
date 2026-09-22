# [H] apparmor: fix use-after-free in rawdata dedup loop

## Summary
Severity: High
Advisory: CVE-2026-63827
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63827
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix use-after-free in rawdata dedup loop

aa_replace_profiles() walks ns->rawdata_list to dedup the incoming
policy blob against entries already attached to existing profiles.
Per the kernel-doc on struct aa_loaddata, list membership does not
hold a reference: profiles hold pcount, and when the last pcount
drops, do_ploaddata_rmfs() is queued on a workqueue that takes
ns->lock and removes the entry. Between dropping the last pcount
and the workqueue running, an entry remains on the list with
pcount == 0.

aa_get_profile_loaddata() is an unconditional kref_get() on
pcount, so when the dedup loop hits such an entry, refcount
hardening reports

  refcount_t: addition on 0; use-after-free.

inside aa_replace_profiles(), and the poisoned counter then
trips "saturated" and "underflow" warnings on the subsequent
uses of the same loaddata.

Before commit a0b7091c4de4 ("apparmor: fix race on rawdata
dereference") the dedup path used a get_unless_zero-style helper
on a single counter, so the existing "if (tmp)" guard was
meaningful. The split-refcount refactor introduced
aa_get_profile_loaddata(), which has plain kref_get() semantics,
and the guard quietly became a no-op.

Introduce aa_get_profile_loaddata_not0(), matching the existing
_not0 convention used by aa_get_profile_not0(), and use it for
the rawdata_list dedup lookup so dying entries are skipped.

Reproduced on x86_64 with v7.1-rc5 in QEMU+KVM running Ubuntu
24.04 + stress-ng 0.17.06:

  stress-ng --apparmor 1 --klog-check --timeout 60s

Without this patch the three refcount_t warnings fire within a
few seconds. With it the same 60 s run is clean. Coverage is a
smoke-test only; a longer soak with CONFIG_KASAN, CONFIG_KCSAN
and CONFIG_PROVE_LOCKING would be welcome from anyone with the
cycles.

## References
- https://git.kernel.org/stable/c/15fd83a1e42ede15070968806bb6c8b1a5170688
- https://git.kernel.org/stable/c/5e34fa9f6f7cd688ae153fff13139a5cf2d42339
- https://git.kernel.org/stable/c/643221da57dbb1a8fd800610331cf1ec27969f71
- https://git.kernel.org/stable/c/6f060496d03e4dc560a40f73770bd08335cb7a27
- https://git.kernel.org/stable/c/a7a2890028f16e5b0af0bb005d80fcb32559cca3
- https://git.kernel.org/stable/c/b17f0c59cc1525765625cf07d0391b7f9c1ed7e5
- https://git.kernel.org/stable/c/c3ca2631073b2cef06824fd2bfc452ff7a1023de
- https://git.kernel.org/stable/c/ce261a20b41db522e320a41bbf1292bf85af66df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63827.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63827
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
