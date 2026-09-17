# [M] CVE-2024-36619

## Summary
Severity: Medium
Advisory: CVE-2024-36619
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36619
Type: osv

## Details
FFmpeg n6.1.1 has a vulnerability in the WAVARC decoder of the libavcodec library which allows for an integer overflow when handling certain block types, leading to a denial-of-service (DoS) condition.

## References
- https://gist.github.com/1047524396/fad68e8251f4e34a1bb838de697d5119
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavcodec/wavarc.c#L651
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36619.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36619
- https://github.com/ffmpeg/ffmpeg/commit/28c7094b25b689185155a6833caf2747b94774a4
