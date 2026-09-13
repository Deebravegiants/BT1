# [H] CVE-2018-1000104

## Summary
Severity: High
Advisory: CVE-2018-1000104
Aliases: GHSA-cghg-jcv6-4v5m
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000104
Type: osv

## Details
A plaintext storage of a password vulnerability exists in Jenkins Coverity Plugin 1.10.0 and earlier in CIMInstance.java that allows an attacker with local file system access or control of a Jenkins administrator's web browser (e.g. malicious extension) to retrieve the configured keystore and private key passwords.

## References
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-260
