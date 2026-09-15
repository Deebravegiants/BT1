# [H] CVE-2020-16122

## Summary
Severity: High
Advisory: CVE-2020-16122
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-07
Source: https://osv.dev/vulnerability/CVE-2020-16122
Type: osv

## Details
PackageKit's apt backend mistakenly treated all local debs as trusted. The apt security model is based on repository trust and not on the contents of individual files. On sites with configured PolicyKit rules this may allow users to install malicious packages.

## References
- https://bugs.launchpad.net/ubuntu/+source/packagekit/+bug/1882098
