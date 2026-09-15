# [M] CVE-2017-2600

## Summary
Severity: Medium
Advisory: CVE-2017-2600
Aliases: GHSA-wj5c-j656-h5fw
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-05-15
Source: https://osv.dev/vulnerability/CVE-2017-2600
Type: osv

## Details
In jenkins before versions 2.44, 2.32.2 node monitor data could be viewed by low privilege users via the remote API. These included system configuration and runtime information of these nodes (SECURITY-343).

## References
- http://www.securityfocus.com/bid/95954
- https://jenkins.io/security/advisory/2017-02-01/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2600
- https://github.com/jenkinsci/jenkins/commit/0f92cd08a19207de2cceb6a2f4e3e9f92fdc0899
