# [M] mm/damon/core: avoid overflow in damon_feed_loop_next_input()

## Summary
Severity: Medium
Advisory: CVE-2024-50270
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50270
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/damon/core: avoid overflow in damon_feed_loop_next_input()

damon_feed_loop_next_input() is inefficient and fragile to overflows. 
Specifically, 'score_goal_diff_bp' calculation can overflow when 'score'
is high.  The calculation is actually unnecessary at all because 'goal' is
a constant of value 10,000.  Calculation of 'compensation' is again
fragile to overflow.  Final calculation of return value for under-achiving
case is again fragile to overflow when the current score is
under-achieving the target.

Add two corner cases handling at the beginning of the function to make the
body easier to read, and rewrite the body of the function to avoid
overflows and the unnecessary bp value calcuation.

## References
- https://git.kernel.org/stable/c/2d339a1f0f16ff5dea58e612ff336f0be0d041e9
- https://git.kernel.org/stable/c/4401e9d10ab0281a520b9f8c220f30f60b5c248f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50270.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
