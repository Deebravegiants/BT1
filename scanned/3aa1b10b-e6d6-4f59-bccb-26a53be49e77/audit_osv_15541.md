# [M] CVE-2019-16990

## Summary
Severity: Medium
Advisory: CVE-2019-16990
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-16990
Type: osv

## Details
In FusionPBX up to v4.5.7, the file app/music_on_hold/music_on_hold.php uses an unsanitized "file" variable coming from the URL, which takes any pathname (base64 encoded) and allows a download of it.

## References
- https://resp3ctblog.wordpress.com/2019/10/19/fusionpbx-path-traversal-3/
- https://github.com/fusionpbx/fusionpbx/commit/95ed18aa9d781f232f5686a9027bb6f677c9b8da
