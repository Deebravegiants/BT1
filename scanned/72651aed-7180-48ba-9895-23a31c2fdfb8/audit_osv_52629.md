# [M] CVE-2021-47659

## Summary
Severity: Medium
Advisory: CVE-2021-47659
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47659
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/plane: Move range check for format_count earlier

While the check for format_count > 64 in __drm_universal_plane_init()
shouldn't be hit (it's a WARN_ON), in its current position it will then
leak the plane->format_types array and fail to call
drm_mode_object_unregister() leaking the modeset identifier. Move it to
the start of the function to avoid allocating those resources in the
first place.

## References
- https://git.kernel.org/stable/c/ad6dd7a2bac86118985c7b3426e175b9d3c1ec4f
- https://git.kernel.org/stable/c/b5cd108143513e4498027b96ec4710702d186f11
- https://git.kernel.org/stable/c/1e29d829ad51d1472dd035487953a6724b56fc33
- https://git.kernel.org/stable/c/4ab7e453a3ee88c274cf97bee9487ab92a66d313
- https://git.kernel.org/stable/c/4b674dd69701c2e22e8e7770c1706a69f3b17269
- https://git.kernel.org/stable/c/787163d19bc3cdc6ca4b96223f62208534d1cf6b
- https://git.kernel.org/stable/c/978e3d023256bfaf34a0033d40c94e8a8e70cf3c
