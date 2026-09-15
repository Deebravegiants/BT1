# [H] CVE-2021-39158

## Summary
Severity: High
Advisory: CVE-2021-39158
Aliases: GHSA-fmpp-8pwg-vwh9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-39158
Type: osv

## Details
NVCaffe's python required dependencies list used to contain `gfortran`version prior to 0.17.4, entry which does not exist in the repository pypi.org. An attacker could potentially have posted malicious files to pypi.org causing a user to install it within NVCaffe.

## References
- https://github.com/NVIDIA/caffe/security/advisories/GHSA-fmpp-8pwg-vwh9
