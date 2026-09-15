# [H] tracing: Verify event formats that have "%*p.."

## Summary
Severity: High
Advisory: CVE-2025-37938
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37938
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Verify event formats that have "%*p.."

The trace event verifier checks the formats of trace events to make sure
that they do not point at memory that is not in the trace event itself or
in data that will never be freed. If an event references data that was
allocated when the event triggered and that same data is freed before the
event is read, then the kernel can crash by reading freed memory.

The verifier runs at boot up (or module load) and scans the print formats
of the events and checks their arguments to make sure that dereferenced
pointers are safe. If the format uses "%*p.." the verifier will ignore it,
and that could be dangerous. Cover this case as well.

Also add to the sample code a use case of "%*pbl".

## References
- https://git.kernel.org/stable/c/03127354027508d076073b020d3070990fd6a958
- https://git.kernel.org/stable/c/04b80d45ecfaf780981d6582899e3ab205e4aa08
- https://git.kernel.org/stable/c/4d11fac941d83509be4e6a21038281d6d96da50c
- https://git.kernel.org/stable/c/6854c87ac823181c810f8c07489ba543260c0023
- https://git.kernel.org/stable/c/c7204fd1758c0caf1938e8a59809a1fdf28a8114
- https://git.kernel.org/stable/c/ea8d7647f9ddf1f81e2027ed305299797299aa03
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37938.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37938
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
