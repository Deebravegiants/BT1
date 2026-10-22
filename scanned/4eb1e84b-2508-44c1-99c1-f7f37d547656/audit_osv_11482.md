# [H] CVE-2017-8033

## Summary
Severity: High
Advisory: CVE-2017-8033
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-8033
Type: osv

## Details
An issue was discovered in the Cloud Controller API in Cloud Foundry Foundation CAPI-release versions prior to v1.35.0 and cf-release versions prior to v268. A filesystem traversal vulnerability exists in the Cloud Controller that allows a space developer to escalate privileges by pushing a specially crafted application that can write arbitrary files to the Cloud Controller VM.

## References
- https://www.cloudfoundry.org/cve-2017-8033/
