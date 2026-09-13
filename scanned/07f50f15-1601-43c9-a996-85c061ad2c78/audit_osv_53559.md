# [C] CVE-2022-4920

## Summary
Severity: Critical
Advisory: CVE-2022-4920
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-07-29
Source: https://osv.dev/vulnerability/CVE-2022-4920
Type: osv

## Details
Heap buffer overflow in Blink in Google Chrome prior to 101.0.4951.41 allowed a remote attacker who convinced a user to engage in specific UI gestures to potentially perform a sandbox escape via a crafted HTML page. (Chromium security severity: High)

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YKLJ3B3D5BCVWE3QNP4N7HHF26OHD567/
- https://chromereleases.googleblog.com/2022/04/stable-channel-update-for-desktop_26.html
- https://crbug.com/1306861
