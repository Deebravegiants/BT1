# [H] rxrpc: proc: size address buffers for %pISpc output

## Summary
Severity: High
Advisory: CVE-2026-31630
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31630
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: proc: size address buffers for %pISpc output

The AF_RXRPC procfs helpers format local and remote socket addresses into
fixed 50-byte stack buffers with "%pISpc".

That is too small for the longest current-tree IPv6-with-port form the
formatter can produce. In lib/vsprintf.c, the compressed IPv6 path uses a
dotted-quad tail not only for v4mapped addresses, but also for ISATAP
addresses via ipv6_addr_is_isatap().

As a result, a case such as

  [ffff:ffff:ffff:ffff:0:5efe:255.255.255.255]:65535

is possible with the current formatter. That is 50 visible characters, so
51 bytes including the trailing NUL, which does not fit in the existing
char[50] buffers used by net/rxrpc/proc.c.

Size the buffers from the formatter's maximum textual form and switch the
call sites to scnprintf().

Changes since v1:
- correct the changelog to cite the actual maximum current-tree case
  explicitly
- frame the proof around the ISATAP formatting path instead of the earlier
  mapped-v4 example

## References
- https://git.kernel.org/stable/c/10ebed83f9f6414af4e85bc85ffaeda7effdd874
- https://git.kernel.org/stable/c/235b2115de892eab2e107a42efa7a4347baaa80b
- https://git.kernel.org/stable/c/386c86412608d3449006a318a662cbcd6ca1f668
- https://git.kernel.org/stable/c/625af53a1564e31bb2df9adc3739df46137f46c1
- https://git.kernel.org/stable/c/a44ce6aa2efb61fe44f2cfab72bb01544bbca272
- https://git.kernel.org/stable/c/db297c78ce537c9ac96f0eda9b25ad72c8caefa9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31630.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31630
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
