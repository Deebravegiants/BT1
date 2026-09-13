# [H] CVE-2018-7166

## Summary
Severity: High
Advisory: CVE-2018-7166
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-7166
Type: osv

## Details
In all versions of Node.js 10 prior to 10.9.0, an argument processing flaw can cause `Buffer.alloc()` to return uninitialized memory. This method is intended to be safe and only return initialized, or cleared, memory. The third argument specifying `encoding` can be passed as a number, this is misinterpreted by `Buffer's` internal "fill" method as the `start` to a fill operation. This flaw may be abused where `Buffer.alloc()` arguments are derived from user input to return uncleared memory blocks that may contain sensitive information.

## References
- https://access.redhat.com/errata/RHSA-2018:2553
- https://nodejs.org/en/blog/vulnerability/august-2018-security-releases/
