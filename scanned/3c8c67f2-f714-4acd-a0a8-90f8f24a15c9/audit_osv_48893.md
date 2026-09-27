# [H] CVE-2018-17480

## Summary
Severity: High
Advisory: CVE-2018-17480
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-11
Source: https://osv.dev/vulnerability/CVE-2018-17480
Type: osv

## Details
Execution of user supplied Javascript during array deserialization leading to an out of bounds write in V8 in Google Chrome prior to 71.0.3578.80 allowed a remote attacker to execute arbitrary code inside a sandbox via a crafted HTML page.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2018-17480
- https://chromereleases.googleblog.com/2018/12/stable-channel-update-for-desktop.html
- https://security.gentoo.org/glsa/201908-18
- https://www.debian.org/security/2018/dsa-4352
- http://www.securityfocus.com/bid/106084
- https://access.redhat.com/errata/RHSA-2018:3803
- https://crbug.com/905940
