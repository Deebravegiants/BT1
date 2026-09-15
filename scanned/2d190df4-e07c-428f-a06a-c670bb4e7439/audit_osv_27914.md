# [H] wifi: mac80211: fix race condition on enabling fast-xmit

## Summary
Severity: High
Advisory: CVE-2024-26779
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26779
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.308, >=4.20.0 <5.4.270, >=5.5.0 <5.10.211, >=5.11.0 <5.15.150, >=5.16.0 <6.1.80, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix race condition on enabling fast-xmit

fast-xmit must only be enabled after the sta has been uploaded to the driver,
otherwise it could end up passing the not-yet-uploaded sta via drv_tx calls
to the driver, leading to potential crashes because of uninitialized drv_priv
data.
Add a missing sta->uploaded check and re-check fast xmit after inserting a sta.

## References
- https://git.kernel.org/stable/c/281280276b70c822f55ce15b661f6d1d3228aaa9
- https://git.kernel.org/stable/c/54b79d8786964e2f840e8a2ec4a9f9a50f3d4954
- https://git.kernel.org/stable/c/5ffab99e070b9f8ae0cf60c3c3602b84eee818dd
- https://git.kernel.org/stable/c/76fad1174a0cae6fc857b9f88b261a2e4f07d587
- https://git.kernel.org/stable/c/85720b69aef177318f4a18efbcc4302228a340e5
- https://git.kernel.org/stable/c/88c18fd06608b3adee547102505d715f21075c9d
- https://git.kernel.org/stable/c/bcbc84af1183c8cf3d1ca9b78540c2185cd85e7f
- https://git.kernel.org/stable/c/eb39bb548bf974acad7bd6780fe11f9e6652d696
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26779.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26779
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
