# [M] CVE-2020-2182

## Summary
Severity: Medium
Advisory: CVE-2020-2182
Aliases: GHSA-7ff8-qfwx-8gx5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-05-06
Source: https://osv.dev/vulnerability/CVE-2020-2182
Type: osv

## Details
Jenkins Credentials Binding Plugin 1.22 and earlier does not mask (i.e., replace with asterisks) secrets containing a `$` character in some circumstances.

## References
- http://www.openwall.com/lists/oss-security/2020/05/06/3
- https://jenkins.io/security/advisory/2020-05-06/#SECURITY-1835
