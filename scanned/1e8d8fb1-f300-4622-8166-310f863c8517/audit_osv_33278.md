# [H] can: hi311x: populate ndo_change_mtu() to prevent buffer overflow

## Summary
Severity: High
Advisory: CVE-2025-39987
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39987
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: hi311x: populate ndo_change_mtu() to prevent buffer overflow

Sending an PF_PACKET allows to bypass the CAN framework logic and to
directly reach the xmit() function of a CAN driver. The only check
which is performed by the PF_PACKET framework is to make sure that
skb->len fits the interface's MTU.

Unfortunately, because the sun4i_can driver does not populate its
net_device_ops->ndo_change_mtu(), it is possible for an attacker to
configure an invalid MTU by doing, for example:

  $ ip link set can0 mtu 9999

After doing so, the attacker could open a PF_PACKET socket using the
ETH_P_CANXL protocol:

	socket(PF_PACKET, SOCK_RAW, htons(ETH_P_CANXL))

to inject a malicious CAN XL frames. For example:

	struct canxl_frame frame = {
		.flags = 0xff,
		.len = 2048,
	};

The CAN drivers' xmit() function are calling can_dev_dropped_skb() to
check that the skb is valid, unfortunately under above conditions, the
malicious packet is able to go through can_dev_dropped_skb() checks:

  1. the skb->protocol is set to ETH_P_CANXL which is valid (the
     function does not check the actual device capabilities).

  2. the length is a valid CAN XL length.

And so, hi3110_hard_start_xmit() receives a CAN XL frame which it is
not able to correctly handle and will thus misinterpret it as a CAN
frame. The driver will consume frame->len as-is with no further
checks.

This can result in a buffer overflow later on in hi3110_hw_tx() on
this line:

	memcpy(buf + HI3110_FIFO_EXT_DATA_OFF,
	       frame->data, frame->len);

Here, frame->len corresponds to the flags field of the CAN XL frame.
In our previous example, we set canxl_frame->flags to 0xff. Because
the maximum expected length is 8, a buffer overflow of 247 bytes
occurs!

Populate net_device_ops->ndo_change_mtu() to ensure that the
interface's MTU can not be set to anything bigger than CAN_MTU. By
fixing the root cause, this prevents the buffer overflow.

## References
- https://git.kernel.org/stable/c/57d332ce8c921d0e340650470bb0c1d707f216ee
- https://git.kernel.org/stable/c/7ab85762274c0fa997f0ef9a2307b2001aae43c4
- https://git.kernel.org/stable/c/8f351db6b2367991f0736b2cff082f5de4872113
- https://git.kernel.org/stable/c/ac1c7656fa717f29fac3ea073af63f0b9919ec9a
- https://git.kernel.org/stable/c/be1b25005fd0f9d4e78bec6695711ef87ee33398
- https://git.kernel.org/stable/c/def814b4ba31b563584061d6895d5ff447d5bc14
- https://git.kernel.org/stable/c/e77fdf9e33a83a08f04ab0cb68c19ddb365a622f
- https://git.kernel.org/stable/c/f2c247e9581024d8b3dd44cbe086bf2bebbef42c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39987.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39987
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
