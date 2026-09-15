# [H] CVE-2018-10112

## Summary
Severity: High
Advisory: CVE-2018-10112
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-16
Source: https://osv.dev/vulnerability/CVE-2018-10112
Type: osv

## Details
An issue was discovered in GEGL through 0.3.32. The gegl_tile_backend_swap_constructed function in buffer/gegl-tile-backend-swap.c allows remote attackers to cause a denial of service (write access violation) or possibly have unspecified other impact via a malformed PNG file that is mishandled during a call to the babl_format_get_bytes_per_pixel function in babl-format.c in babl 0.1.46.

## References
- https://bugzilla.gnome.org/show_bug.cgi?id=795249
- https://github.com/xiaoqx/pocs/tree/master/gegl
