# [H] CVE-2019-5789

## Summary
Severity: High
Advisory: CVE-2019-5789
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-05-23
Source: https://osv.dev/vulnerability/CVE-2019-5789
Type: osv

## Details
An integer overflow that leads to a use-after-free in WebMIDI in Google Chrome on Windows prior to 73.0.3683.75 allowed a remote attacker who had compromised the renderer process to execute arbitrary code via a crafted HTML page.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00085.html
- https://crbug.com/921581
- https://chromereleases.googleblog.com/2019/03/stable-channel-update-for-desktop_12.html
