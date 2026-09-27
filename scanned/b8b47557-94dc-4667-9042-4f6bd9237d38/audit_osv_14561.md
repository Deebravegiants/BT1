# [C] CVE-2019-1010308

## Summary
Severity: Critical
Advisory: CVE-2019-1010308
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-15
Source: https://osv.dev/vulnerability/CVE-2019-1010308
Type: osv

## Details
Aquaverde GmbH Aquarius CMS prior to version 4.1.1 is affected by: Incorrect Access Control. The impact is: The access to the log file is not restricted. It contains sensitive information like passwords etc. The component is: log file. The attack vector is: open the file.

## References
- https://github.com/aquaverde/aquarius-core
- https://github.com/aquaverde/aquarius-core/commit/e1af89aa9df07ea265d879518ede9eb98aa494e0
