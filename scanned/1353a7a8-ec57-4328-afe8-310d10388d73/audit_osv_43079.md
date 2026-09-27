# [H] bpf: Guard conntrack opts error writes

## Summary
Severity: High
Advisory: CVE-2026-72423
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72423
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Guard conntrack opts error writes

The conntrack lookup and allocation kfuncs take an opts pointer
together with an opts__sz argument. The verifier checks only the memory
range described by opts__sz, but the wrappers unconditionally write
opts->error whenever the internal lookup or allocation helper returns an
error.

For an invalid size smaller than the end of opts->error, that write can
land outside the verifier-checked range. Keep returning NULL for invalid
arguments, but only report the error through opts->error when the
supplied size includes the field.

This preserves error reporting for the supported 12-byte and 16-byte
layouts, and for other invalid sizes that still include opts->error.

## References
- https://git.kernel.org/stable/c/6f6183a39533d727deaa5061cadae6dd9e6744d0
- https://git.kernel.org/stable/c/dd74c80203842a21b2ebb9f70d1260d9aa20fa05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72423.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72423
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
