# [C] btrfs: fix double free of qgroup record after failure to add delayed ref head

## Summary
Severity: Critical
Advisory: CVE-2025-68359
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68359
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix double free of qgroup record after failure to add delayed ref head

In the previous code it was possible to incur into a double kfree()
scenario when calling add_delayed_ref_head(). This could happen if the
record was reported to already exist in the
btrfs_qgroup_trace_extent_nolock() call, but then there was an error
later on add_delayed_ref_head(). In this case, since
add_delayed_ref_head() returned an error, the caller went to free the
record. Since add_delayed_ref_head() couldn't set this kfree'd pointer
to NULL, then kfree() would have acted on a non-NULL 'record' object
which was pointing to memory already freed by the callee.

The problem comes from the fact that the responsibility to kfree the
object is on both the caller and the callee at the same time. Hence, the
fix for this is to shift the ownership of the 'qrecord' object out of
the add_delayed_ref_head(). That is, we will never attempt to kfree()
the given object inside of this function, and will expect the caller to
act on the 'qrecord' object on its own. The only exception where the
'qrecord' object cannot be kfree'd is if it was inserted into the
tracing logic, for which we already have the 'qrecord_inserted_ret'
boolean to account for this. Hence, the caller has to kfree the object
only if add_delayed_ref_head() reports not to have inserted it on the
tracing logic.

As a side-effect of the above, we must guarantee that
'qrecord_inserted_ret' is properly initialized at the start of the
function, not at the end, and then set when an actual insert
happens. This way we avoid 'qrecord_inserted_ret' having an invalid
value on an early exit.

The documentation from the add_delayed_ref_head() has also been updated
to reflect on the exact ownership of the 'qrecord' object.

## References
- https://git.kernel.org/stable/c/364685c4c2d9c9f4408d95451bcf42fdeebc3ebb
- https://git.kernel.org/stable/c/725e46298876a2cc1f1c3fb22ba69d29102c3ddf
- https://git.kernel.org/stable/c/7617680769e3119dfb3b43a2b7c287ce2242211c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68359.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68359
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
