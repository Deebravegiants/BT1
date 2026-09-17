# [H] media: mc, v4l2: serialize REINIT and REQBUFS with req_queue_mutex

## Summary
Severity: High
Advisory: CVE-2026-31473
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31473
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mc, v4l2: serialize REINIT and REQBUFS with req_queue_mutex

MEDIA_REQUEST_IOC_REINIT can run concurrently with VIDIOC_REQBUFS(0)
queue teardown paths. This can race request object cleanup against vb2
queue cancellation and lead to use-after-free reports.

We already serialize request queueing against STREAMON/OFF with
req_queue_mutex. Extend that serialization to REQBUFS, and also take
the same mutex in media_request_ioctl_reinit() so REINIT is in the
same exclusion domain.

This keeps request cleanup and queue cancellation from running in
parallel for request-capable devices.

## References
- https://git.kernel.org/stable/c/1a0d9083c24fbd5d22f7100f09d11e4d696a5f01
- https://git.kernel.org/stable/c/2c685e99efb3b3bd2b78699fba6b1cf321975db0
- https://git.kernel.org/stable/c/331242998a7ade5c2f65e14988901614629f3db5
- https://git.kernel.org/stable/c/585fd9a2063dacce8b2820f675ef23d5d17434c5
- https://git.kernel.org/stable/c/72b9e81e0203f03c40f3adb457f55bd4c8eb112d
- https://git.kernel.org/stable/c/bef4f4a88b73e4cc550d25f665b8a9952af22773
- https://git.kernel.org/stable/c/cf2023e84f0888f96f4b65dc0804e7f3651969c1
- https://git.kernel.org/stable/c/d8549a453d5bdc0a71de66ad47a1106703406a56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31473.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31473
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
