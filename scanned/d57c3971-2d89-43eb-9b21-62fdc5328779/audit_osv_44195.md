# [H] Input: focaltech - fix array out-of-bounds in focaltech_process_rel_packet

## Summary
Severity: High
Advisory: CVE-2026-80574
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80574
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Input: focaltech - fix array out-of-bounds in focaltech_process_rel_packet

Make finger2 (and also finger1) unsigned, so that if the finger index in
the packet is 0 then subtracting 1 creates an array index which overflows
above the existing check for FOC_MAX_FINGERS, as the existing comment says
it should, instead of writing to state->fingers[-1].

## References
- https://git.kernel.org/stable/c/063b4c6a6f3fc01bca085c442000c9c100fdbd93
- https://git.kernel.org/stable/c/1842e47126816e56d30c4f856f9854fd7831066c
- https://git.kernel.org/stable/c/296736076b3fd078742651c719555a488624023a
- https://git.kernel.org/stable/c/6f6d5fe29efdf5001bc146fc292e6592cace93eb
- https://git.kernel.org/stable/c/81b07470cb2937ceb74b00be88151582a322433b
- https://git.kernel.org/stable/c/83c265bfc084d77e2171d4b67362150ab38c935b
- https://git.kernel.org/stable/c/bb502d79acb9ac1e0a77fa8bc7b7b4729140b11f
- https://git.kernel.org/stable/c/ca92c98b806839c108995b2bbff7061515bdfb53
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80574.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80574
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
