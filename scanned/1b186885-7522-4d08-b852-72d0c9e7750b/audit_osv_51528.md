# [H] CVE-2021-31523

## Summary
Severity: High
Advisory: CVE-2021-31523
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2021-31523
Type: osv

## Details
The Debian xscreensaver 5.42+dfsg1-1 package for XScreenSaver has cap_net_raw enabled for the /usr/libexec/xscreensaver/sonar file, which allows local users to gain privileges because this is arguably incompatible with the design of the Mesa 3D Graphics library dependency.

## References
- http://www.openwall.com/lists/oss-security/2021/04/21/3
- https://www.openwall.com/lists/oss-security/2021/04/17/1
