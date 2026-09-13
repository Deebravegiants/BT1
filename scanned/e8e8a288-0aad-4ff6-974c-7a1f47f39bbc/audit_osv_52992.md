# [M] CVE-2022-2479

## Summary
Severity: Medium
Advisory: CVE-2022-2479
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2022-07-28
Source: https://osv.dev/vulnerability/CVE-2022-2479
Type: osv

## Details
Insufficient validation of untrusted input in File in Google Chrome on Android prior to 103.0.5060.134 allowed an attacker who convinced a user to install a malicious app to obtain potentially sensitive information from internal file directories via a crafted HTML page.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PQKT7EGDD2P3L7S3NXEDDRCPK4NNZNWJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YKLJ3B3D5BCVWE3QNP4N7HHF26OHD567/
- https://chromereleases.googleblog.com/2022/07/stable-channel-update-for-desktop_19.html
- https://security.gentoo.org/glsa/202208-35
- https://crbug.com/1329987
