# [M] HCI Connection Creation Dangling State Reference Re-use

## Summary
Severity: Medium
Advisory: CVE-2023-1902
Aliases: CVE-2023-2234, GHSA-fx9g-8fr2-q899
CVSS: 5.9 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-1902
Type: osv

## Details
The bluetooth HCI host layer logic not clearing a global reference to a state pointer after handling connection events may allow a malicious HCI Controller to cause the use of a dangling reference in the host layer, leading to a crash (DoS) or potential RCE on the Host layer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1902.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-fx9g-8fr2-q899
- https://nvd.nist.gov/vuln/detail/CVE-2023-1902
- https://github.com/zephyrproject-rtos/zephyr
