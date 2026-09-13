# [M] Possible to retrieve uncrypted firmware image

## Summary
Severity: Medium
Advisory: CVE-2022-0553
Aliases: GHSA-wrj2-9vj9-rrcp
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-11
Source: https://osv.dev/vulnerability/CVE-2022-0553
Type: osv

## Details
There is no check to see if slot 0 is being uploaded from the device to the host. When using encrypted images this means the unencrypted firmware can be retrieved easily.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0553.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-wrj2-9vj9-rrcp
- https://nvd.nist.gov/vuln/detail/CVE-2022-0553
