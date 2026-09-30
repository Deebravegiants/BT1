# [H] fork: only invoke khugepaged, ksm hooks if no error

## Summary
Severity: High
Advisory: CVE-2024-50263
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-11
Source: https://osv.dev/vulnerability/CVE-2024-50263
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

fork: only invoke khugepaged, ksm hooks if no error

There is no reason to invoke these hooks early against an mm that is in an
incomplete state.

The change in commit d24062914837 ("fork: use __mt_dup() to duplicate
maple tree in dup_mmap()") makes this more pertinent as we may be in a
state where entries in the maple tree are not yet consistent.

Their placement early in dup_mmap() only appears to have been meaningful
for early error checking, and since functionally it'd require a very small
allocation to fail (in practice 'too small to fail') that'd only occur in
the most dire circumstances, meaning the fork would fail or be OOM'd in
any case.

Since both khugepaged and KSM tracking are there to provide optimisations
to memory performance rather than critical functionality, it doesn't
really matter all that much if, under such dire memory pressure, we fail
to register an mm with these.

As a result, we follow the example of commit d2081b2bf819 ("mm:
khugepaged: make khugepaged_enter() void function") and make ksm_fork() a
void function also.

We only expose the mm to these functions once we are done with them and
only if no error occurred in the fork operation.

## References
- https://git.kernel.org/stable/c/3b85aa0da8cd01173b9afd1f70080fbb9576c4b0
- https://git.kernel.org/stable/c/985da552a98e27096444508ce5d853244019111f
- https://project-zero.issues.chromium.org/issues/373391951
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50263.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50263
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
