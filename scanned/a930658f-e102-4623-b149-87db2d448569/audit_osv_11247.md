# [C] CVE-2017-6889

## Summary
Severity: Critical
Advisory: CVE-2017-6889
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-15
Source: https://osv.dev/vulnerability/CVE-2017-6889
Type: osv

## Details
An integer overflow error within the "foveon_load_camf()" function (dcraw_foveon.c) in LibRaw-demosaic-pack-GPL2 before 0.18.2 can be exploited to cause a heap-based buffer overflow.

## References
- https://secuniaresearch.flexerasoftware.com/advisories/75000/
- https://github.com/LibRaw/LibRaw-demosaic-pack-GPL2/commit/194f592e205990ea8fce72b6c571c14350aca716
