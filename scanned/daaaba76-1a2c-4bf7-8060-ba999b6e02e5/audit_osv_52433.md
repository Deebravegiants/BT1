# [M] CVE-2021-47444

## Summary
Severity: Medium
Advisory: CVE-2021-47444
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47444
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/edid: In connector_bad_edid() cap num_of_ext by num_blocks read

In commit e11f5bd8228f ("drm: Add support for DP 1.4 Compliance edid
corruption test") the function connector_bad_edid() started assuming
that the memory for the EDID passed to it was big enough to hold
`edid[0x7e] + 1` blocks of data (1 extra for the base block). It
completely ignored the fact that the function was passed `num_blocks`
which indicated how much memory had been allocated for the EDID.

Let's fix this by adding a bounds check.

This is important for handling the case where there's an error in the
first block of the EDID. In that case we will call
connector_bad_edid() without having re-allocated memory based on
`edid[0x7e]`.

## References
- https://git.kernel.org/stable/c/09f3946bb452918dbfb1982add56f9ffaae393dc
- https://git.kernel.org/stable/c/97794170b696856483f74b47bfb6049780d2d3a0
- https://git.kernel.org/stable/c/a7b45024f66f9ec769e8dbb1a51ae83cd05929c7
