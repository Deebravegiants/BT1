# [C] CVE-2020-27853

## Summary
Severity: Critical
Advisory: CVE-2020-27853
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-27
Source: https://osv.dev/vulnerability/CVE-2020-27853
Type: osv

## Details
Wire before 2020-10-16 allows remote attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a format string. This affects Wire AVS (Audio, Video, and Signaling) 5.3 through 6.x before 6.4, the Wire Secure Messenger application before 3.49.918 for Android, and the Wire Secure Messenger application before 3.61 for iOS. This occurs via the value parameter to sdp_media_set_lattr in peerflow/sdp.c.

## References
- http://github.security.telekom.com/2020/11/wire-secure-messenger-format-string-vulnerability.html
- https://github.com/wireapp/wire-audio-video-signaling/issues/23#issuecomment-710075689
