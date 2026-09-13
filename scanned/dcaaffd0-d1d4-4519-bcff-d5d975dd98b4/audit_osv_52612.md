# [H] CVE-2021-47642

## Summary
Severity: High
Advisory: CVE-2021-47642
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47642
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

video: fbdev: nvidiafb: Use strscpy() to prevent buffer overflow

Coverity complains of a possible buffer overflow. However,
given the 'static' scope of nvidia_setup_i2c_bus() it looks
like that can't happen after examiniing the call sites.

CID 19036 (#1 of 1): Copy into fixed size buffer (STRING_OVERFLOW)
1. fixed_size_dest: You might overrun the 48-character fixed-size string
  chan->adapter.name by copying name without checking the length.
2. parameter_as_source: Note: This defect has an elevated risk because the
  source argument is a parameter of the current function.
 89        strcpy(chan->adapter.name, name);

Fix this warning by using strscpy() which will silence the warning and
prevent any future buffer overflows should the names used to identify the
channel become much longer.

## References
- https://git.kernel.org/stable/c/055cdd2e7b992921424d4daaa285ced787fb205f
- https://git.kernel.org/stable/c/08dff482012758935c185532b1ad7d584785a86e
- https://git.kernel.org/stable/c/47e5533adf118afaf06d25a3e2aaaab89371b1c5
- https://git.kernel.org/stable/c/6a5226e544ac043bb2d8dc1bfe8920d02282f7cd
- https://git.kernel.org/stable/c/9ff2f7294ab0f011cd4d1b7dcd9a07d8fdf72834
- https://git.kernel.org/stable/c/37a1a2e6eeeb101285cd34e12e48a881524701aa
- https://git.kernel.org/stable/c/41baa86b6c802cdc6ab8ff2d46c083c9be93de81
- https://git.kernel.org/stable/c/580e5d3815474b8349250c25c16416585a72c7fe
- https://git.kernel.org/stable/c/72dd5c46a152136712a55bf026a9aa8c1b12b60d
