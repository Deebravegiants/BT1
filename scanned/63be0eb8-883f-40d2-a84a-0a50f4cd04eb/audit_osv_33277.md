# [H] can: sun4i_can: populate ndo_change_mtu() to prevent buffer overflow

## Summary
Severity: High
Advisory: CVE-2025-39986
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39986
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: sun4i_can: populate ndo_change_mtu() to prevent buffer overflow

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

And so, sun4ican_start_xmit() receives a CAN XL frame which it is not
able to correctly handle and will thus misinterpret it as a CAN frame.

This can result in a buffer overflow. The driver will consume cf->len
as-is with no further checks on this line:

	dlc = cf->len;

Here, cf->len corresponds to the flags field of the CAN XL frame. In
our previous example, we set canxl_frame->flags to 0xff. Because the
maximum expected length is 8, a buffer overflow of 247 bytes occurs a
couple line below when doing:

	for (i = 0; i < dlc; i++)
		writel(cf->data[i], priv->base + (dreg + i * 4));

Populate net_device_ops->ndo_change_mtu() to ensure that the
interface's MTU can not be set to anything bigger than CAN_MTU. By
fixing the root cause, this prevents the buffer overflow.

## References
- https://git.kernel.org/stable/c/063539db42203b29d5aa2adf0cae3d68c646a6b6
- https://git.kernel.org/stable/c/2e423e1990f3972cbea779883fef52c2f2acb858
- https://git.kernel.org/stable/c/4f382cc887adca8478b9d3e6b81aa6698a95fff4
- https://git.kernel.org/stable/c/60463a1c138900494cb3adae41142a11cd8feb3c
- https://git.kernel.org/stable/c/61da0bd4102c459823fbe6b8b43b01fb6ace4a22
- https://git.kernel.org/stable/c/7f7b21026a6febdb749f6f6f950427245aa86cce
- https://git.kernel.org/stable/c/a61ff7ac93270d20ca426c027d6d01c8ac8e904c
- https://git.kernel.org/stable/c/de77841652e57afbc46e9e1dbf51ee364fc008e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39986.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
