# [H] CVE-2018-1000410

## Summary
Severity: High
Advisory: CVE-2018-1000410
Aliases: GHSA-53jp-gmwc-jwf6
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/CVE-2018-1000410
Type: osv

## Details
An information exposure vulnerability exists in Jenkins 2.145 and earlier, LTS 2.138.1 and earlier, and the Stapler framework used by these releases, in core/src/main/java/org/kohsuke/stapler/RequestImpl.java, core/src/main/java/hudson/model/Descriptor.java that allows attackers with Overall/Administer permission or access to the local file system to obtain credentials entered by users if the form submission could not be successfully processed.

## References
- http://www.securityfocus.com/bid/106532
- https://jenkins.io/security/advisory/2018-10-10/#SECURITY-765
