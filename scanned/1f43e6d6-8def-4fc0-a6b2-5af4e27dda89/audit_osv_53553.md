# [H] CVE-2022-4914

## Summary
Severity: High
Advisory: CVE-2022-4914
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-29
Source: https://osv.dev/vulnerability/CVE-2022-4914
Type: osv

## Details
Heap buffer overflow in PrintPreview in Google Chrome prior to 104.0.5112.79 allowed an attacker who convinced a user to install a malicious extension to potentially exploit heap corruption via a crafted HTML page. (Chromium security severity: Medium)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YKLJ3B3D5BCVWE3QNP4N7HHF26OHD567/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://chromereleases.googleblog.com/2022/08/stable-channel-update-for-desktop.html
- https://crbug.com/1232402
