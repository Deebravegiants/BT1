# [H] CVE-2021-47046

## Summary
Severity: High
Advisory: CVE-2021-47046
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47046
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix off by one in hdmi_14_process_transaction()

The hdcp_i2c_offsets[] array did not have an entry for
HDCP_MESSAGE_ID_WRITE_CONTENT_STREAM_TYPE so it led to an off by one
read overflow.  I added an entry and copied the 0x0 value for the offset
from similar code in drivers/gpu/drm/amd/display/modules/hdcp/hdcp_ddc.c.

I also declared several of these arrays as having HDCP_MESSAGE_ID_MAX
entries.  This doesn't change the code, but it's just a belt and
suspenders approach to try future proof the code.

## References
- https://git.kernel.org/stable/c/080bd41d6478a64edf96704fddcda52b1fd5fed7
- https://git.kernel.org/stable/c/403c4528e5887af3deb9838cb77a557631d1e138
- https://git.kernel.org/stable/c/6a58310d5d1e5b02d0fc9b393ba540c9367bced5
- https://git.kernel.org/stable/c/8e6fafd5a22e7a2eb216f5510db7aab54cc545c1
