# [H] usb: cdns3: fix memory double free when handle zero packet

## Summary
Severity: High
Advisory: CVE-2024-26748
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26748
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: cdns3: fix memory double free when handle zero packet

829  if (request->complete) {
830          spin_unlock(&priv_dev->lock);
831          usb_gadget_giveback_request(&priv_ep->endpoint,
832                                    request);
833          spin_lock(&priv_dev->lock);
834  }
835
836  if (request->buf == priv_dev->zlp_buf)
837      cdns3_gadget_ep_free_request(&priv_ep->endpoint, request);

Driver append an additional zero packet request when queue a packet, which
length mod max packet size is 0. When transfer complete, run to line 831,
usb_gadget_giveback_request() will free this requestion. 836 condition is
true, so cdns3_gadget_ep_free_request() free this request again.

Log:

[ 1920.140696][  T150] BUG: KFENCE: use-after-free read in cdns3_gadget_giveback+0x134/0x2c0 [cdns3]
[ 1920.140696][  T150]
[ 1920.151837][  T150] Use-after-free read at 0x000000003d1cd10b (in kfence-#36):
[ 1920.159082][  T150]  cdns3_gadget_giveback+0x134/0x2c0 [cdns3]
[ 1920.164988][  T150]  cdns3_transfer_completed+0x438/0x5f8 [cdns3]

Add check at line 829, skip call usb_gadget_giveback_request() if it is
additional zero length packet request. Needn't call
usb_gadget_giveback_request() because it is allocated in this driver.

## References
- https://git.kernel.org/stable/c/1e204a8e9eb514e22a6567fb340ebb47df3f3a48
- https://git.kernel.org/stable/c/3a2a909942b5335b7ea66366d84261b3ed5f89c8
- https://git.kernel.org/stable/c/5fd9e45f1ebcd57181358af28506e8a661a260b3
- https://git.kernel.org/stable/c/70e8038813f9d3e72df966748ebbc40efe466019
- https://git.kernel.org/stable/c/92d20406a3d4ff3e8be667c79209dc9ed31df5b3
- https://git.kernel.org/stable/c/9a52b694b066f299d8b9800854a8503457a8b64c
- https://git.kernel.org/stable/c/aad6132ae6e4809e375431f8defd1521985e44e7
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26748.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
