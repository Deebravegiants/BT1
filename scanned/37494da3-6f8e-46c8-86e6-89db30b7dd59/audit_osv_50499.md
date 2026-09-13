# [H] CVE-2020-16041

## Summary
Severity: High
Advisory: CVE-2020-16041
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-01-08
Source: https://osv.dev/vulnerability/CVE-2020-16041
Type: osv

## Details
Out of bounds read in networking in Google Chrome prior to 87.0.4280.88 allowed a remote attacker who had compromised the renderer process to obtain potentially sensitive information from process memory via a crafted HTML page.

## References
- http://packetstormsecurity.com/files/161581/Chrome-DataElement-Out-Of-Bounds-Read.html
- https://chromereleases.googleblog.com/2020/12/stable-channel-update-for-desktop.html
- https://crbug.com/1151865
