# [M] CVE-2021-47381

## Summary
Severity: Medium
Advisory: CVE-2021-47381
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47381
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: Fix DSP oops stack dump output contents

Fix @buf arg given to hex_dump_to_buffer() and stack address used
in dump error output.

## References
- https://git.kernel.org/stable/c/a6bb576ead074ca6fa3b53cb1c5d4037a23de81b
- https://git.kernel.org/stable/c/ac4dfccb96571ca03af7cac64b7a0b2952c97f3a
