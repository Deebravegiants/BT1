# [C] CVE-2016-5713

## Summary
Severity: Critical
Advisory: CVE-2016-5713
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/CVE-2016-5713
Type: osv

## Details
Versions of Puppet Agent prior to 1.6.0 included a version of the Puppet Execution Protocol (PXP) agent that passed environment variables through to Puppet runs. This could allow unauthorized code to be loaded. This bug was first introduced in Puppet Agent 1.3.0.

## References
- https://puppet.com/security/cve/cve-2016-5713
