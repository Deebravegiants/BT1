# [H] CVE-2023-40339

## Summary
Severity: High
Advisory: CVE-2023-40339
Aliases: GHSA-pv2g-vm98-vjxf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-16
Source: https://osv.dev/vulnerability/CVE-2023-40339
Type: osv

## Details
Jenkins Config File Provider Plugin 952.va_544a_6234b_46 and earlier does not mask (i.e., replace with asterisks) credentials specified in configuration files when they're written to the build log.

## References
- http://www.openwall.com/lists/oss-security/2023/08/16/3
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3090
