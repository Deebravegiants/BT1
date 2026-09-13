# [C] CVE-2024-35366

## Summary
Severity: Critical
Advisory: CVE-2024-35366
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-35366
Type: osv

## Details
FFmpeg n6.1.1 is Integer Overflow. The vulnerability exists in the parse_options function of sbgdec.c within the libavformat module. When parsing certain options, the software does not adequately validate the input. This allows for negative duration values to be accepted without proper bounds checking.

## References
- https://gist.github.com/1047524396/1e72f170d58c2547ebd4db4cdf6cfabf
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/sbgdec.c#L389
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35366.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35366
- https://github.com/ffmpeg/ffmpeg/commit/0bed22d597b78999151e3bde0768b7fe763fc2a6
