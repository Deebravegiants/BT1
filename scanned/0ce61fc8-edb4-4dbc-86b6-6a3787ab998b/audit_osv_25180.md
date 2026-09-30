# [C] CVE-2023-31634

## Summary
Severity: Critical
Advisory: CVE-2023-31634
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2023-31634
Type: osv

## Details
In TeslaMate before 1.27.2, there is unauthorized access to port 4000 for remote viewing and operation of user data. After accessing the IP address for the TeslaMate instance, an attacker can switch the port to 3000 to enter Grafana for remote operations. At that time, the default username and password can be used to enter the Grafana management console without logging in, a related issue to CVE-2022-23126.

## References
- https://github.com/XC9409/CVE-2023-31634/blob/main/PoC
- https://github.com/adriankumpf/teslamate/releases/tag/v1.27.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31634.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31634
