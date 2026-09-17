# [M] CVE-2024-36616

## Summary
Severity: Medium
Advisory: CVE-2024-36616
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36616
Type: osv

## Details
An integer overflow in the component /libavformat/westwood_vqa.c of FFmpeg n6.1.1 allows attackers to cause a denial of service in the application via a crafted VQA file.

## References
- https://gist.github.com/1047524396/ded3e1509d8296ec4a91817867d108e0
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/westwood_vqa.c#L265
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36616.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36616
- https://github.com/ffmpeg/ffmpeg/commit/86f73277bf014e2ce36dd2594f1e0fb8b3bd6661
