# [M] CVE-2021-47583

## Summary
Severity: Medium
Advisory: CVE-2021-47583
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47583
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mxl111sf: change mutex_init() location

Syzbot reported, that mxl111sf_ctrl_msg() uses uninitialized
mutex. The problem was in wrong mutex_init() location.

Previous mutex_init(&state->msg_lock) call was in ->init() function, but
dvb_usbv2_init() has this order of calls:

	dvb_usbv2_init()
	  dvb_usbv2_adapter_init()
	    dvb_usbv2_adapter_frontend_init()
	      props->frontend_attach()

	  props->init()

Since mxl111sf_* devices call mxl111sf_ctrl_msg() in ->frontend_attach()
internally we need to initialize state->msg_lock before
frontend_attach(). To achieve it, ->probe() call added to all mxl111sf_*
devices, which will simply initiaize mutex.

## References
- https://git.kernel.org/stable/c/b99bdf127af91d53919e96292c05f737c45ea59a
- https://git.kernel.org/stable/c/44870a9e7a3c24acbb3f888b2a7cc22c9bdf7e7f
- https://git.kernel.org/stable/c/4b2d9600b31f9ba7adbc9f3c54a068615d27b390
- https://git.kernel.org/stable/c/8c6fdf62bfe1bc72bfceeaf832ef7499c7ed09ba
- https://git.kernel.org/stable/c/96f182c9f48b984447741f054ec301fdc8517035
