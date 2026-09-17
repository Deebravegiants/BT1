# [H] drm/i915/active: Fix misuse of non-idle barriers as fence trackers

## Summary
Severity: High
Advisory: CVE-2023-53087
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53087
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.176, >=5.11.0 <5.15.104, >=5.16.0 <6.1.21, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/active: Fix misuse of non-idle barriers as fence trackers

Users reported oopses on list corruptions when using i915 perf with a
number of concurrently running graphics applications.  Root cause analysis
pointed at an issue in barrier processing code -- a race among perf open /
close replacing active barriers with perf requests on kernel context and
concurrent barrier preallocate / acquire operations performed during user
context first pin / last unpin.

When adding a request to a composite tracker, we try to reuse an existing
fence tracker, already allocated and registered with that composite.  The
tracker we obtain may already track another fence, may be an idle barrier,
or an active barrier.

If the tracker we get occurs a non-idle barrier then we try to delete that
barrier from a list of barrier tasks it belongs to.  However, while doing
that we don't respect return value from a function that performs the
barrier deletion.  Should the deletion ever fail, we would end up reusing
the tracker still registered as a barrier task.  Since the same structure
field is reused with both fence callback lists and barrier tasks list,
list corruptions would likely occur.

Barriers are now deleted from a barrier tasks list by temporarily removing
the list content, traversing that content with skip over the node to be
deleted, then populating the list back with the modified content.  Should
that intentionally racy concurrent deletion attempts be not serialized,
one or more of those may fail because of the list being temporary empty.

Related code that ignores the results of barrier deletion was initially
introduced in v5.4 by commit d8af05ff38ae ("drm/i915: Allow sharing the
idle-barrier from other kernel requests").  However, all users of the
barrier deletion routine were apparently serialized at that time, then the
issue didn't exhibit itself.  Results of git bisect with help of a newly
developed igt@gem_barrier_race@remote-request IGT test indicate that list
corruptions might start to appear after commit 311770173fac ("drm/i915/gt:
Schedule request retirement when timeline idles"), introduced in v5.5.

Respect results of barrier deletion attempts -- mark the barrier as idle
only if successfully deleted from the list.  Then, before proceeding with
setting our fence as the one currently tracked, make sure that the tracker
we've got is not a non-idle barrier.  If that check fails then don't use
that tracker but go back and try to acquire a new, usable one.

v3: use unlikely() to document what outcome we expect (Andi),
  - fix bad grammar in commit description.
v2: no code changes,
  - blame commit 311770173fac ("drm/i915/gt: Schedule request retirement
    when timeline idles"), v5.5, not commit d8af05ff38ae ("drm/i915: Allow
    sharing the idle-barrier from other kernel requests"), v5.4,
  - reword commit description.

(cherry picked from commit 506006055769b10d1b2b4e22f636f3b45e0e9fc7)

## References
- https://git.kernel.org/stable/c/5c7591b8574c52c56b3994c2fbef1a3a311b5715
- https://git.kernel.org/stable/c/5e784a7d07af42057c0576fb647b482f4cb0dc2c
- https://git.kernel.org/stable/c/6ab7d33617559cced63d467928f478ea5c459021
- https://git.kernel.org/stable/c/9159db27fb19bbf1c91b5c9d5285e66cc96cc5ff
- https://git.kernel.org/stable/c/e0e6b416b25ee14716f3549e0cbec1011b193809
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53087.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
