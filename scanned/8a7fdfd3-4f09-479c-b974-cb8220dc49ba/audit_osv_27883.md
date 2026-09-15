# [H] smb: Fix regression in writes when non-standard maximum write size negotiated

## Summary
Severity: High
Advisory: CVE-2024-26692
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26692
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: Fix regression in writes when non-standard maximum write size negotiated

The conversion to netfs in the 6.3 kernel caused a regression when
maximum write size is set by the server to an unexpected value which is
not a multiple of 4096 (similarly if the user overrides the maximum
write size by setting mount parm "wsize", but sets it to a value that
is not a multiple of 4096).  When negotiated write size is not a
multiple of 4096 the netfs code can skip the end of the final
page when doing large sequential writes, causing data corruption.

This section of code is being rewritten/removed due to a large
netfs change, but until that point (ie for the 6.3 kernel until now)
we can not support non-standard maximum write sizes.

Add a warning if a user specifies a wsize on mount that is not
a multiple of 4096 (and round down), also add a change where we
round down the maximum write size if the server negotiates a value
that is not a multiple of 4096 (we also have to check to make sure that
we do not round it down to zero).

## References
- https://git.kernel.org/stable/c/4145ccff546ea868428b3e0fe6818c6261b574a9
- https://git.kernel.org/stable/c/4860abb91f3d7fbaf8147d54782149bb1fc45892
- https://git.kernel.org/stable/c/63c35afd50e28b49c5b75542045a8c42b696dab9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26692.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26692
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
