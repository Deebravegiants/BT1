# [M] CVE-2017-4970

## Summary
Severity: Medium
Advisory: CVE-2017-4970
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-06-13
Source: https://osv.dev/vulnerability/CVE-2017-4970
Type: osv

## Details
An issue was discovered in Cloud Foundry Foundation cf-release v255 and Staticfile buildpack versions v1.4.0 - v1.4.3. A regression introduced in the Static file build pack causes the Staticfile.auth configuration to be ignored when the Static file file is not present in the application root. Applications containing a Staticfile.auth file but not a Static file had their basic auth turned off when an operator upgraded the Static file build pack in the foundation to one of the vulnerable versions. Note that Static file applications without a Static file are technically misconfigured, and will not successfully detect unless the Static file build pack is explicitly specified.

## References
- https://www.cloudfoundry.org/cve-2017-4970/
