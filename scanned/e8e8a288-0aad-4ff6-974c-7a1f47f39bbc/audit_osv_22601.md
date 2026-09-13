# [M] CVE-2022-3287

## Summary
Severity: Medium
Advisory: CVE-2022-3287
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-28
Source: https://osv.dev/vulnerability/CVE-2022-3287
Type: osv

## Details
When creating an OPERATOR user account on the BMC, the redfish plugin saved the auto-generated password to /etc/fwupd/redfish.conf without proper restriction, allowing any user on the system to read the same configuration file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3287.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3287
- https://github.com/fwupd/fwupd/commit/ea676855f2119e36d433fbd2ed604039f53b2091
