# [M] CVE-2017-17555

## Summary
Severity: Medium
Advisory: CVE-2017-17555
Aliases: PYSEC-2017-77
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/CVE-2017-17555
Type: osv

## Details
The swri_audio_convert function in audioconvert.c in FFmpeg libswresample through 3.0.101, as used in FFmpeg 3.4.1, aubio 0.4.6, and other products, allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted audio file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00012.html
- https://github.com/IvanCql/vulnerability/blob/master/An%20NULL%20pointer%20dereference%28DoS%29%20Vulnerability%20was%20found%20in%20function%20swri_audio_convert%20of%20ffmpeg%20libswresample.md
