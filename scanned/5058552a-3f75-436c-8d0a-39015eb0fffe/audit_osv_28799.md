# [C] CVE-2024-36671

## Summary
Severity: Critical
Advisory: CVE-2024-36671
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36671
Type: osv

## Details
nodemcu before v3.0.0-release_20240225 was discovered to contain an integer overflow via the getnum function at /modules/struct.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36671.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36671
- https://github.com/nodemcu/nodemcu-firmware/issues/3626
- https://github.com/nodemcu/nodemcu-firmware/commit/193fe3593eb1537667179089535cdb7457327887#diff-5c3fa597431eda03ac3339ae6bf7f05e1a50d6fc7333679ec38e21b337cb6721
- https://github.com/nodemcu/nodemcu-firmware/pull/3633
- https://github.com/nodemcu/nodemcu-firmware/pull/3634
- https://github.com/nodemcu/nodemcu-firmware/pull/3635
