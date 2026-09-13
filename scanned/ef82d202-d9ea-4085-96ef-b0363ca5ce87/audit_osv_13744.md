# [C] CVE-2018-25071

## Summary
Severity: Critical
Advisory: CVE-2018-25071
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2018-25071
Type: osv

## Details
A vulnerability was found in roxlukas LMeve up to 0.1.58. It has been rated as critical. Affected by this issue is the function insert_log of the file wwwroot/ccpwgl/proxy.php. The manipulation of the argument fetch leads to sql injection. Upgrading to version 0.1.59-beta is able to address this issue. The patch is identified as c25ff7fe83a2cda1fcb365b182365adc3ffae332. It is recommended to upgrade the affected component. VDB-217610 is the identifier assigned to this vulnerability.

## References
- https://github.com/roxlukas/lmeve/releases/tag/0.1.59-beta
- https://vuldb.com/?ctiid.217610
- https://vuldb.com/?id.217610
- https://github.com/roxlukas/lmeve/commit/c25ff7fe83a2cda1fcb365b182365adc3ffae332
