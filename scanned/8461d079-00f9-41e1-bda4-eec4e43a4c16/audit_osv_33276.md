# [H] can: mcba_usb: populate ndo_change_mtu() to prevent buffer overflow

## Summary
Severity: High
Advisory: CVE-2025-39985
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39985
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: mcba_usb: populate ndo_change_mtu() to prevent buffer overflow

Sending an PF_PACKET allows to bypass the CAN framework logic and to
directly reach the xmit() function of a CAN driver. The only check
which is performed by the PF_PACKET framework is to make sure that
skb->len fits the interface's MTU.

Unfortunately, because the mcba_usb driver does not populate its
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

And so, mcba_usb_start_xmit() receives a CAN XL frame which it is not
able to correctly handle and will thus misinterpret it as a CAN frame.

This can result in a buffer overflow. The driver will consume cf->len
as-is with no further checks on these lines:

	usb_msg.dlc = cf->len;

	memcpy(usb_msg.data, cf->data, usb_msg.dlc);

Here, cf->len corresponds to the flags field of the CAN XL frame. In
our previous example, we set canxl_frame->flags to 0xff. Because the
maximum expected length is 8, a buffer overflow of 247 bytes occurs!

Populate net_device_ops->ndo_change_mtu() to ensure that the
interface's MTU can not be set to anything bigger than CAN_MTU. By
fixing the root cause, this prevents the buffer overflow.

## References
- https://git.kernel.org/stable/c/0fa9303c4b9493727e0d3a6ac3729300e3013930
- https://git.kernel.org/stable/c/17c8d794527f01def0d1c8b7dc2d7b8d34fed0e6
- https://git.kernel.org/stable/c/3664ae91b26d1fd7e4cee9cde17301361f4c89d5
- https://git.kernel.org/stable/c/37aed407496bf6de8910e588edb04d2435fa7011
- https://git.kernel.org/stable/c/6b9fb82df8868dbe9ffea5874b8d35f951faedbb
- https://git.kernel.org/stable/c/6eec67bfb25637f9b51e584cf59ddace59925bc8
- https://git.kernel.org/stable/c/b638c3fb0f163e69785ceddb3b434a9437878bec
- https://git.kernel.org/stable/c/ca4e51359608e1f29bf1f2c33c3ddf775b6b7ed1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39985.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39985
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
