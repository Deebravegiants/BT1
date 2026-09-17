# [M] bpf: Mark raw_tp arguments with PTR_MAYBE_NULL

## Summary
Severity: Medium
Advisory: CVE-2024-56702
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56702
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Mark raw_tp arguments with PTR_MAYBE_NULL

Arguments to a raw tracepoint are tagged as trusted, which carries the
semantics that the pointer will be non-NULL.  However, in certain cases,
a raw tracepoint argument may end up being NULL. More context about this
issue is available in [0].

Thus, there is a discrepancy between the reality, that raw_tp arguments
can actually be NULL, and the verifier's knowledge, that they are never
NULL, causing explicit NULL checks to be deleted, and accesses to such
pointers potentially crashing the kernel.

To fix this, mark raw_tp arguments as PTR_MAYBE_NULL, and then special
case the dereference and pointer arithmetic to permit it, and allow
passing them into helpers/kfuncs; these exceptions are made for raw_tp
programs only. Ensure that we don't do this when ref_obj_id > 0, as in
that case this is an acquired object and doesn't need such adjustment.

The reason we do mask_raw_tp_trusted_reg logic is because other will
recheck in places whether the register is a trusted_reg, and then
consider our register as untrusted when detecting the presence of the
PTR_MAYBE_NULL flag.

To allow safe dereference, we enable PROBE_MEM marking when we see loads
into trusted pointers with PTR_MAYBE_NULL.

While trusted raw_tp arguments can also be passed into helpers or kfuncs
where such broken assumption may cause issues, a future patch set will
tackle their case separately, as PTR_TO_BTF_ID (without PTR_TRUSTED) can
already be passed into helpers and causes similar problems. Thus, they
are left alone for now.

It is possible that these checks also permit passing non-raw_tp args
that are trusted PTR_TO_BTF_ID with null marking. In such a case,
allowing dereference when pointer is NULL expands allowed behavior, so
won't regress existing programs, and the case of passing these into
helpers is the same as above and will be dealt with later.

Also update the failure case in tp_btf_nullable selftest to capture the
new behavior, as the verifier will no longer cause an error when
directly dereference a raw tracepoint argument marked as __nullable.

  [0]: https://lore.kernel.org/bpf/ZrCZS6nisraEqehw@jlelli-thinkpadt14gen4.remote.csb

## References
- https://git.kernel.org/stable/c/3634d4a310820567fc634bf8f1ee2b91378773e8
- https://git.kernel.org/stable/c/c9b91d2d54175f781ad2c361cb2ac2c0e29b14b6
- https://git.kernel.org/stable/c/cb4158ce8ec8a5bb528cc1693356a5eb8058094d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56702.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56702
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
