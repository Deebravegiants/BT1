# [M] CVE-2017-8312

## Summary
Severity: Medium
Advisory: CVE-2017-8312
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-8312
Type: osv

## Details
Heap out-of-bound read in ParseJSS in VideoLAN VLC due to missing check of string length allows attackers to read heap uninitialized data via a crafted subtitles file.

## References
- http://git.videolan.org/?p=vlc.git%3Ba=blobdiff%3Bf=modules/demux/subtitle.c%3Bh=5e4fcdb7f25b2819f5441156c7c0ea2a7d112ca3%3Bhp=2a75fbfb7c3f56b24b2e4498bbb8fe0aa2575974%3Bhb=611398fc8d32f3fe4331f60b220c52ba3557beaa%3Bhpb=075bc7169b05b004fa0250e4a4ce5516b05487a9
- http://www.debian.org/security/2017/dsa-3899
- http://www.securityfocus.com/bid/98631
- https://security.gentoo.org/glsa/201707-10
