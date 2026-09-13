# [H] CVE-2025-62491

## Summary
Severity: High
Advisory: CVE-2025-62491
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62491
Type: osv

## Details
A Use-After-Free (UAF) vulnerability exists in the QuickJS engine's standard library when iterating over the global list of unhandled rejected promises (ts->rejected_promise_list).

  *  The function js_std_promise_rejection_check attempts to iterate over the rejected_promise_list to report unhandled rejections using a standard list loop.


  *  The reason for a promise rejection is processed inside the loop, including calling js_std_dump_error1(ctx, rp->reason).


  *  If the promise rejection reason is an Error object that defines a custom property getter (e.g., via Object.defineProperty), this getter is executed during the error dumping process.


  *  The malicious custom getter can execute JavaScript code that calls catch() on the same rejected promise being processed.


  *  Calling catch() internally triggers js_std_promise_rejection_tracker, which then removes and frees the current promise entry (JSRejectedPromiseEntry) from the rejected_promise_list.


  *  Since the list iteration continues using the now-freed memory pointer (el), the subsequent loop access results in a Use-After-Free condition.

## References
- https://bellard.org/quickjs/Changelog
- https://issuetracker.google.com/434195203
