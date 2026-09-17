# [H] can: etas_es58x: populate ndo_change_mtu() to prevent buffer overflow

## Summary
Severity: High
Advisory: CVE-2025-39988
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39988
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: etas_es58x: populate ndo_change_mtu() to prevent buffer overflow

Sending an PF_PACKET allows to bypass the CAN framework logic and to
directly reach the xmit() function of a CAN driver. The only check
which is performed by the PF_PACKET framework is to make sure that
skb->len fits the interface's MTU.

Unfortunately, because the etas_es58x driver does not populate its
net_device_ops->ndo_change_mtu(), it is possible for an attacker to
configure an invalid MTU by doing, for example:

  $ ip link set can0 mtu 9999

After doing so, the attacker could open a PF_PACKET socket using the
ETH_P_CANXL protocol:

	socket(PF_PACKET, SOCK_RAW, htons(ETH_P_CANXL));

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

And so, es58x_start_xmit() receives a CAN XL frame which it is not
able to correctly handle and will thus misinterpret it as a CAN(FD)
frame.

This can result in a buffer overflow. For example, using the es581.4
variant, the frame will be dispatched to es581_4_tx_can_msg(), go
through the last check at the beginning of this function:

	if (can_is_canfd_skb(skb))
		return -EMSGSIZE;

and reach this line:

	memcpy(tx_can_msg->data, cf->data, cf->len);

Here, cf->len corresponds to the flags field of the CAN XL frame. In
our previous example, we set canxl_frame->flags to 0xff. Because the
maximum expected length is 8, a buffer overflow of 247 bytes occurs!

Populate net_device_ops->ndo_change_mtu() to ensure that the
interface's MTU can not be set to anything bigger than CAN_MTU or
CANFD_MTU (depending on the device capabilities). By fixing the root
cause, this prevents the buffer overflow.

## References
- https://git.kernel.org/stable/c/38c0abad45b190a30d8284a37264d2127a6ec303
- https://git.kernel.org/stable/c/72de0facc50afdb101fb7197d880407f1abfc77f
- https://git.kernel.org/stable/c/b26cccd87dcddc47b450a40f3b1ac3fe346efcff
- https://git.kernel.org/stable/c/c4e582e686c4d683c87f2b4a316385b3d81d370f
- https://git.kernel.org/stable/c/cbc1de71766f326a44bb798aeae4a7ef4a081cc9
- https://git.kernel.org/stable/c/e587af2c89ecc6382c518febea52fa9ba81e47c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39988.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39988
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
