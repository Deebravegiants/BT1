# [H] CVE-2017-8048

## Summary
Severity: High
Advisory: CVE-2017-8048
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-04
Source: https://osv.dev/vulnerability/CVE-2017-8048
Type: osv

## Details
In Cloud Foundry capi-release versions 1.33.0 and later, prior to 1.42.0 and cf-release versions 268 and later, prior to 274, the original fix for CVE-2017-8033 introduces an API regression that allows a space developer to execute arbitrary code on the Cloud Controller VM by pushing a specially crafted application. NOTE: 274 resolves the vulnerability but has a serious bug that is fixed in 275.

## References
- https://www.cloudfoundry.org/cve-2017-8048/
