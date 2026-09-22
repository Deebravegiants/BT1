# [M] CVE-2017-18925

## Summary
Severity: Medium
Advisory: CVE-2017-18925
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-10-26
Source: https://osv.dev/vulnerability/CVE-2017-18925
Type: osv

## Details
opentmpfiles through 0.3.1 allows local users to take ownership of arbitrary files because d entries are mishandled and allow a symlink attack.

## References
- https://github.com/OpenRC/opentmpfiles/issues/4
