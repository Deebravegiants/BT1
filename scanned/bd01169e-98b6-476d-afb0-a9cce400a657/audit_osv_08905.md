# [H] CVE-2016-6639

## Summary
Severity: High
Advisory: CVE-2016-6639
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-09-18
Source: https://osv.dev/vulnerability/CVE-2016-6639
Type: osv

## Details
Cloud Foundry PHP Buildpack (aka php-buildpack) before 4.3.18 and PHP Buildpack Cf-release before 242, as used in Pivotal Cloud Foundry (PCF) Elastic Runtime before 1.6.38 and 1.7.x before 1.7.19 and other products, place the .profile file in the htdocs directory, which might allow remote attackers to obtain sensitive information via an HTTP GET request for this file.

## References
- https://pivotal.io/security/cve-2016-6639
- https://github.com/cloudfoundry/php-buildpack/commit/e2db3ccd4812e0c0aba20720fc51789d981aba67
