# [H] firmware: cs_dsp: Prevent buffer overrun when processing V2 alg headers

## Summary
Severity: High
Advisory: CVE-2024-41038
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41038
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: cs_dsp: Prevent buffer overrun when processing V2 alg headers

Check that all fields of a V2 algorithm header fit into the available
firmware data buffer.

The wmfw V2 format introduced variable-length strings in the algorithm
block header. This means the overall header length is variable, and the
position of most fields varies depending on the length of the string
fields. Each field must be checked to ensure that it does not overflow
the firmware data buffer.

As this ia bugfix patch, the fixes avoid making any significant change to
the existing code. This makes it easier to review and less likely to
introduce new bugs.

## References
- https://git.kernel.org/stable/c/014239b9971d79421a0ba652579e1ca1b7b57b6d
- https://git.kernel.org/stable/c/2163aff6bebbb752edf73f79700f5e2095f3559e
- https://git.kernel.org/stable/c/6619aa48a011364e9f29083cc76368e6acfe5b11
- https://git.kernel.org/stable/c/76ea8e13aaefdfda6e5601323d6ea5340359dcfa
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41038.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41038
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
