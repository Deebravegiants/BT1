# [H] can: softing: fw_parse(): validate firmware record spans

## Summary
Severity: High
Advisory: CVE-2026-80706
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80706
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: softing: fw_parse(): validate firmware record spans

fw_parse() reads a fixed record header, a firmware-provided payload,
and a trailing checksum without knowing the end of the firmware blob. A
truncated record can therefore make those reads exceed the blob.

The same record also supplies addresses and lengths for writes into
DPRAM. The generic loader uses wrap-prone mixed signed arithmetic for its
bounds check, while the application loader does not bound the staging
copy at all.

Pass the firmware end to the parser and validate the full source record.
Use a signed wide offset for generic DPRAM records and validate the
application staging span against the mapped DPRAM before copying.

## References
- https://git.kernel.org/stable/c/2ee477e541a6d5e434d6a4041c6b677ab42e1d82
- https://git.kernel.org/stable/c/808ed899dcf8bdef66894fda5eb7ee4bb0eb8dc1
- https://git.kernel.org/stable/c/84c850b08fc0d671c245144b619683129b55690a
- https://git.kernel.org/stable/c/856d6cb04e5407523566b075841dcd6423757d1c
- https://git.kernel.org/stable/c/ad331e26fd213a19fee0de18cdacd67b7ff5b478
- https://git.kernel.org/stable/c/ae588e5b9cc268de1aabf30f939f0870717ca164
- https://git.kernel.org/stable/c/d0eac0ea7cf493e787fd7b4a556e43ef03cb4b50
- https://git.kernel.org/stable/c/f6d9a6a9512430b395a1940d7b216394fd02d30b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80706.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80706
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
