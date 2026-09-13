# [M] CVE-2019-2391

## Summary
Severity: Medium
Advisory: CVE-2019-2391
Aliases: GHSA-4jwp-vfvf-657p
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-03-31
Source: https://osv.dev/vulnerability/CVE-2019-2391
Type: osv

## Details
Incorrect parsing of certain JSON input may result in js-bson not correctly serializing BSON. This may cause unexpected application behaviour including data disclosure. This issue affects: MongoDB Inc. js-bson library version 1.1.3 and prior to.

## References
- https://github.com/mongodb/js-bson/releases/tag/v1.1.4
