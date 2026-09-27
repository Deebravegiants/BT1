# [H] CVE-2016-1000352

## Summary
Severity: High
Advisory: CVE-2016-1000352
Aliases: GHSA-w285-wf9q-5w69
CVSS: 7.4 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2016-1000352
Type: osv

## Details
In the Bouncy Castle JCE Provider version 1.55 and earlier the ECIES implementation allowed the use of ECB mode. This mode is regarded as unsafe and support for it has been removed from the provider.

## References
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:2927
- https://security.netapp.com/advisory/ntap-20181127-0004/
- https://github.com/bcgit/bc-java/commit/9385b0ebd277724b167fe1d1456e3c112112be1f
