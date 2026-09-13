# [H] drm/i915: Fix request ref counting during error capture & debugfs dump

## Summary
Severity: High
Advisory: CVE-2023-52981
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52981
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Fix request ref counting during error capture & debugfs dump

When GuC support was added to error capture, the reference counting
around the request object was broken. Fix it up.

The context based search manages the spinlocking around the search
internally. So it needs to grab the reference count internally as
well. The execlist only request based search relies on external
locking, so it needs an external reference count but within the
spinlock not outside it.

The only other caller of the context based search is the code for
dumping engine state to debugfs. That code wasn't previously getting
an explicit reference at all as it does everything while holding the
execlist specific spinlock. So, that needs updaing as well as that
spinlock doesn't help when using GuC submission. Rather than trying to
conditionally get/put depending on submission model, just change it to
always do the get/put.

v2: Explicitly document adding an extra blank line in some dense code
(Andy Shevchenko). Fix multiple potential null pointer derefs in case
of no request found (some spotted by Tvrtko, but there was more!).
Also fix a leaked request in case of !started and another in
__guc_reset_context now that intel_context_find_active_request is
actually reference counting the returned request.
v3: Add a _get suffix to intel_context_find_active_request now that it
grabs a reference (Daniele).
v4: Split the intel_guc_find_hung_context change to a separate patch
and rename intel_context_find_active_request_get to
intel_context_get_active_request (Tvrtko).
v5: s/locking/reference counting/ in commit message (Tvrtko)

(cherry picked from commit 3700e353781e27f1bc7222f51f2cc36cbeb9b4ec)

## References
- https://git.kernel.org/stable/c/86d8ddc74124c3fdfc139f246ba6da15e45e86e3
- https://git.kernel.org/stable/c/9467397f417dd7b5d0db91452f0474e79716a527
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52981.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52981
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
