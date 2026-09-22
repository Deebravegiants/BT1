# [H] CVE-2023-3732

## Summary
Severity: High
Advisory: CVE-2023-3732
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-3732
Type: osv

## Details
Out of bounds memory access in Mojo in Google Chrome prior to 115.0.5790.98 allowed a remote attacker who had compromised the renderer process to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: High)

## References
- http://packetstormsecurity.com/files/174223/Chrome-IPCZ-FragmentDescriptors-Missing-Validation.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://chromereleases.googleblog.com/2023/07/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/202401-34
- https://crbug.com/1450899
