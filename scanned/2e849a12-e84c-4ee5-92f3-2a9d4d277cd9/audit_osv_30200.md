# [H] media: qcom: camss: Remove use_count guard in stop_streaming

## Summary
Severity: High
Advisory: CVE-2024-50175
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50175
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: qcom: camss: Remove use_count guard in stop_streaming

The use_count check was introduced so that multiple concurrent Raw Data
Interfaces RDIs could be driven by different virtual channels VCs on the
CSIPHY input driving the video pipeline.

This is an invalid use of use_count though as use_count pertains to the
number of times a video entity has been opened by user-space not the number
of active streams.

If use_count and stream-on count don't agree then stop_streaming() will
break as is currently the case and has become apparent when using CAMSS
with libcamera's released softisp 0.3.

The use of use_count like this is a bit hacky and right now breaks regular
usage of CAMSS for a single stream case. Stopping qcam results in the splat
below, and then it cannot be started again and any attempts to do so fails
with -EBUSY.

[ 1265.509831] WARNING: CPU: 5 PID: 919 at drivers/media/common/videobuf2/videobuf2-core.c:2183 __vb2_queue_cancel+0x230/0x2c8 [videobuf2_common]
...
[ 1265.510630] Call trace:
[ 1265.510636]  __vb2_queue_cancel+0x230/0x2c8 [videobuf2_common]
[ 1265.510648]  vb2_core_streamoff+0x24/0xcc [videobuf2_common]
[ 1265.510660]  vb2_ioctl_streamoff+0x5c/0xa8 [videobuf2_v4l2]
[ 1265.510673]  v4l_streamoff+0x24/0x30 [videodev]
[ 1265.510707]  __video_do_ioctl+0x190/0x3f4 [videodev]
[ 1265.510732]  video_usercopy+0x304/0x8c4 [videodev]
[ 1265.510757]  video_ioctl2+0x18/0x34 [videodev]
[ 1265.510782]  v4l2_ioctl+0x40/0x60 [videodev]
...
[ 1265.510944] videobuf2_common: driver bug: stop_streaming operation is leaving buffer 0 in active state
[ 1265.511175] videobuf2_common: driver bug: stop_streaming operation is leaving buffer 1 in active state
[ 1265.511398] videobuf2_common: driver bug: stop_streaming operation is leaving buffer 2 in active st

One CAMSS specific way to handle multiple VCs on the same RDI might be:

- Reference count each pipeline enable for CSIPHY, CSID, VFE and RDIx.
- The video buffers are already associated with msm_vfeN_rdiX so
  release video buffers when told to do so by stop_streaming.
- Only release the power-domains for the CSIPHY, CSID and VFE when
  their internal refcounts drop.

Either way refusing to release video buffers based on use_count is
erroneous and should be reverted. The silicon enabling code for selecting
VCs is perfectly fine. Its a "known missing feature" that concurrent VCs
won't work with CAMSS right now.

Initial testing with this code didn't show an error but, SoftISP and "real"
usage with Google Hangouts breaks the upstream code pretty quickly, we need
to do a partial revert and take another pass at VCs.

This commit partially reverts commit 89013969e232 ("media: camss: sm8250:
Pipeline starting and stopping for multiple virtual channels")

## References
- https://git.kernel.org/stable/c/25f18cb1b673220b76a86ebef8e7fb79bd303b27
- https://git.kernel.org/stable/c/a975db8aea152f9907aa53a7f517e557ccb40da3
- https://git.kernel.org/stable/c/c2218a82f795dc3d0b6210bcaa3d9c5ca736fcd9
- https://git.kernel.org/stable/c/d7d4dde3decef1b5aa1f5c390147f79aae412dee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50175.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50175
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
