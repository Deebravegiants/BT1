# [M] CVE-2016-1677

## Summary
Severity: Medium
Advisory: CVE-2016-1677
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-06-05
Source: https://osv.dev/vulnerability/CVE-2016-1677
Type: osv

## Details
uri.js in Google V8 before 5.1.281.26, as used in Google Chrome before 51.0.2704.63, uses an incorrect array type, which allows remote attackers to obtain sensitive information by calling the decodeURI function and leveraging "type confusion."

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00005.html
- http://www.securityfocus.com/bid/90876
- http://www.securitytracker.com/id/1035981
- https://codereview.chromium.org/1936083002
- https://crbug.com/602970
- http://www.debian.org/security/2016/dsa-3590
- http://www.ubuntu.com/usn/USN-2992-1
- https://access.redhat.com/errata/RHSA-2016:1190
- https://security.gentoo.org/glsa/201607-07
- http://googlechromereleases.blogspot.com/2016/05/stable-channel-update_25.html
