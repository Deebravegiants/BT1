# [M] CVE-2021-47409

## Summary
Severity: Medium
Advisory: CVE-2021-47409
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47409
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc2: check return value after calling platform_get_resource()

It will cause null-ptr-deref if platform_get_resource() returns NULL,
we need check the return value.

## References
- https://git.kernel.org/stable/c/8b9c1c33e51d0959f2aec573dfbac0ffd3f5c0b7
- https://git.kernel.org/stable/c/a7182993dd8e09f96839ddc3ac54f9b37370d282
- https://git.kernel.org/stable/c/2754fa3b73df7d0ae042f3ed6cfd9df9042f6262
- https://git.kernel.org/stable/c/337f00a0bc62d7cb7d10ec0b872c79009a1641df
- https://git.kernel.org/stable/c/4b7f4a0eb92bf37bea4cd838c7f83ea42823ca8b
- https://git.kernel.org/stable/c/856e6e8e0f9300befa87dde09edb578555c99a82
