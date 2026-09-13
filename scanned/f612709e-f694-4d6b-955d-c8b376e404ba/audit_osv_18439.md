# [H] CVE-2020-27687

## Summary
Severity: High
Advisory: CVE-2020-27687
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-18
Source: https://osv.dev/vulnerability/CVE-2020-27687
Type: osv

## Details
ThingsBoard before v3.2 is vulnerable to Host header injection in password-reset emails. This allows an attacker to send malicious links in password-reset emails to victims, pointing to an attacker-controlled server. Lack of validation of the Host header allows this to happen.

## References
- https://github.com/thingsboard/thingsboard/commits/master
- https://gist.github.com/vin01/26a8bb13233acd9425e7575a7ad4c936
