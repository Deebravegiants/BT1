# [M] CVE-2023-34323

## Summary
Severity: Medium
Advisory: CVE-2023-34323
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-34323
Type: osv

## Details
When a transaction is committed, C Xenstored will first check
the quota is correct before attempting to commit any nodes.  It would
be possible that accounting is temporarily negative if a node has
been removed outside of the transaction.

Unfortunately, some versions of C Xenstored are assuming that the
quota cannot be negative and are using assert() to confirm it.  This
will lead to C Xenstored crash when tools are built without -DNDEBUG
(this is the default).

## References
- http://xenbits.xen.org/xsa/advisory-440.html
- https://xenbits.xenproject.org/xsa/advisory-440.html
