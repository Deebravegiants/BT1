# [M] CVE-2021-20180

## Summary
Severity: Medium
Advisory: CVE-2021-20180
Aliases: GHSA-fh5v-5f35-2rv2, PYSEC-2026-618
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-20180
Type: osv

## Details
A flaw was found in ansible module where credentials are disclosed in the console log by default and not protected by the security feature when using the bitbucket_pipeline_variable module. This flaw allows an attacker to steal bitbucket_pipeline credentials. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1915808
