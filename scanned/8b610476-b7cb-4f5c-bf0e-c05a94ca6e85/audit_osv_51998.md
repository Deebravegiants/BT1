# [M] CVE-2021-46941

## Summary
Severity: Medium
Advisory: CVE-2021-46941
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46941
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3: core: Do core softreset when switch mode


According to the programming guide, to switch mode for DRD controller,
the driver needs to do the following.

To switch from device to host:
1. Reset controller with GCTL.CoreSoftReset
2. Set GCTL.PrtCapDir(host mode)
3. Reset the host with USBCMD.HCRESET
4. Then follow up with the initializing host registers sequence

To switch from host to device:
1. Reset controller with GCTL.CoreSoftReset
2. Set GCTL.PrtCapDir(device mode)
3. Reset the device with DCTL.CSftRst
4. Then follow up with the initializing registers sequence

Currently we're missing step 1) to do GCTL.CoreSoftReset and step 3) of
switching from host to device. John Stult reported a lockup issue seen
with HiKey960 platform without these steps[1]. Similar issue is observed
with Ferry's testing platform[2].

So, apply the required steps along with some fixes to Yu Chen's and John
Stultz's version. The main fixes to their versions are the missing wait
for clocks synchronization before clearing GCTL.CoreSoftReset and only
apply DCTL.CSftRst when switching from host to device.

[1] https://lore.kernel.org/linux-usb/20210108015115.27920-1-john.stultz@linaro.org/
[2] https://lore.kernel.org/linux-usb/0ba7a6ba-e6a7-9cd4-0695-64fc927e01f1@gmail.com/

## References
- https://git.kernel.org/stable/c/1c10fd60c8595ea7ff7e29d3cf1fa88069941da3
- https://git.kernel.org/stable/c/800f58217626c8b147aa40660e572ed8a0d56e3b
- https://git.kernel.org/stable/c/f88359e1588b85cf0e8209ab7d6620085f3441d9
- https://git.kernel.org/stable/c/fce7bbcd07d59ac30dba8ce225316b3b4c1c7b50
