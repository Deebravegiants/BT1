# [M] CVE-2020-36786

## Summary
Severity: Medium
Advisory: CVE-2020-36786
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36786
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: [next] staging: media: atomisp: fix memory leak of object flash

In the case where the call to lm3554_platform_data_func returns an
error there is a memory leak on the error return path of object
flash.  Fix this by adding an error return path that will free
flash and rename labels fail2 to fail3 and fail1 to fail2.

## References
- https://git.kernel.org/stable/c/cc4cc2fb5aaf9adb83c02211eb13b16cfcb7ba64
- https://git.kernel.org/stable/c/27d2eab69f7da8e94e4751ac5c6d22d809275484
- https://git.kernel.org/stable/c/4f0f37d03cde8f4341df8454f9b40a67fda94a33
- https://git.kernel.org/stable/c/6045b01dd0e3cd3759eafe7f290ed04c957500b1
