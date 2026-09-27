# [H] iio: backend: fix out-of-bound write

## Summary
Severity: High
Advisory: CVE-2025-38484
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38484
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: backend: fix out-of-bound write

The buffer is set to 80 character. If a caller write more characters,
count is truncated to the max available space in "simple_write_to_buffer".
But afterwards a string terminator is written to the buffer at offset count
without boundary check. The zero termination is written OUT-OF-BOUND.

Add a check that the given buffer is smaller then the buffer to prevent.

## References
- https://git.kernel.org/stable/c/01e941aa7f5175125df4ac5d3aab099961525602
- https://git.kernel.org/stable/c/6eea9f7648ddb9e4903735a1f77cf196c957aa38
- https://git.kernel.org/stable/c/da9374819eb3885636934c1006d450c3cb1a02ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38484.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38484
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
