# [C] CVE-2021-4297

## Summary
Severity: Critical
Advisory: CVE-2021-4297
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-01
Source: https://osv.dev/vulnerability/CVE-2021-4297
Type: osv

## Details
A vulnerability has been found in trampgeek jobe up to 1.6.4 and classified as problematic. This vulnerability affects the function runs_post of the file application/controllers/Restapi.php. The manipulation of the argument sourcefilename leads to an unknown weakness. Upgrading to version 1.6.5 is able to address this issue. The patch is identified as 694da5013dbecc8d30dd83e2a83e78faadf93771. It is recommended to upgrade the affected component. VDB-217174 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?ctiid.217174
- https://vuldb.com/?id.217174
- https://github.com/trampgeek/jobe/commit/694da5013dbecc8d30dd83e2a83e78faadf93771
- https://github.com/trampgeek/jobe/issues/46
