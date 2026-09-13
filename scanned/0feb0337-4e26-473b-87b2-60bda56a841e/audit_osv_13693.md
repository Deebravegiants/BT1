# [M] CVE-2018-20839

## Summary
Severity: Medium
Advisory: CVE-2018-20839
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-05-17
Source: https://osv.dev/vulnerability/CVE-2018-20839
Type: osv

## Details
systemd 242 changes the VT1 mode upon a logout, which allows attackers to read cleartext passwords in certain circumstances, such as watching a shutdown, or using Ctrl-Alt-F1 and Ctrl-Alt-F2. This occurs because the KDGKBMODE (aka current keyboard mode) check is mishandled.

## References
- http://www.securityfocus.com/bid/108389
- https://security.netapp.com/advisory/ntap-20190530-0002/
- https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/1803993
- https://github.com/systemd/systemd/commit/9725f1a10f80f5e0ae7d9b60547458622aeb322f
- https://github.com/systemd/systemd/pull/12378
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
