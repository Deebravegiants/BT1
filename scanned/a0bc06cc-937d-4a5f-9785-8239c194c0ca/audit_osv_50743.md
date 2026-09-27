# [M] CVE-2020-36777

## Summary
Severity: Medium
Advisory: CVE-2020-36777
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2020-36777
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: dvbdev: Fix memory leak in dvb_media_device_free()

dvb_media_device_free() is leaking memory. Free `dvbdev->adapter->conn`
before setting it to NULL, as documented in include/media/media-device.h:
"The media_entity instance itself must be freed explicitly by the driver
if required."

## References
- https://git.kernel.org/stable/c/bf9a40ae8d722f281a2721779595d6df1c33a0bf
- https://git.kernel.org/stable/c/cd89f79be5d553c78202f686e8e4caa5fbe94e98
- https://git.kernel.org/stable/c/cede24d13be6c2a62be6d7ceea63c2719b0cfa82
- https://git.kernel.org/stable/c/06854b943e0571ccbd7ad0a529babed1a98ff275
- https://git.kernel.org/stable/c/32168ca1f123316848fffb85d059860adf3c409f
- https://git.kernel.org/stable/c/43263fd43083e412311fa764cd04a727b0c6a749
- https://git.kernel.org/stable/c/9185b3b1c143b8da409c19ac5a785aa18d67a81b
- https://git.kernel.org/stable/c/9ad15e214fcd73694ea51967d86055f47b802066
