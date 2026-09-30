# [C] CVE-2018-25070

## Summary
Severity: Critical
Advisory: CVE-2018-25070
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2018-25070
Type: osv

## Details
A vulnerability has been found in polterguy Phosphorus Five up to 8.2 and classified as critical. This vulnerability affects the function csv.Read of the file plugins/extras/p5.mysql/NonQuery.cs of the component CSV Import. The manipulation leads to sql injection. Upgrading to version 8.3 is able to address this issue. The patch is identified as c179a3d0703db55cfe0cb939b89593f2e7a87246. It is recommended to upgrade the affected component. VDB-217606 is the identifier assigned to this vulnerability.

## References
- https://github.com/polterguy/phosphorusfive/releases/tag/v8.3
- https://vuldb.com/?id.217606
- https://vuldb.com/?ctiid.217606
- https://github.com/polterguy/phosphorusfive/commit/c179a3d0703db55cfe0cb939b89593f2e7a87246
