# [M] CVE-2017-6888

## Summary
Severity: Medium
Advisory: CVE-2017-6888
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/CVE-2017-6888
Type: osv

## Details
An error in the "read_metadata_vorbiscomment_()" function (src/libFLAC/stream_decoder.c) in FLAC version 1.3.2 can be exploited to cause a memory leak via a specially crafted FLAC file.

## References
- https://git.xiph.org/?p=flac.git%3Ba=commit%3Bh=4f47b63e9c971e6391590caf00a0f2a5ed612e67
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/33W6XZAAEJYRGU3XYHRO7XSYEA7YACUB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KNZYTAU5UWBVXVJ4VHDWPR66ZVDLQZRE/
- https://lists.debian.org/debian-lts-announce/2021/01/msg00001.html
- https://secuniaresearch.flexerasoftware.com/advisories/82639/
- https://secuniaresearch.flexerasoftware.com/secunia_research/2017-7/
