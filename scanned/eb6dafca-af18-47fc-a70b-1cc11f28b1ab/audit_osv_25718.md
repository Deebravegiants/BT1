# [H] bt: mesh: vulnerability in provisioning protocol implementation on provisionee side

## Summary
Severity: High
Advisory: CVE-2023-4258
Aliases: GHSA-m34c-cp63-rwh7
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-09-25
Source: https://osv.dev/vulnerability/CVE-2023-4258
Type: osv

## Details
In Bluetooth mesh implementation If provisionee has a public key that is sent OOB then during provisioning it can be sent back and will be accepted by provisionee.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4258.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-m34c-cp63-rwh7
- https://nvd.nist.gov/vuln/detail/CVE-2023-4258
- https://github.com/zephyrproject-rtos/zephyr
