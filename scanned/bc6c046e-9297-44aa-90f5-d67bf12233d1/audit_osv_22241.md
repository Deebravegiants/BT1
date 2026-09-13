# [H] CVE-2022-24035

## Summary
Severity: High
Advisory: CVE-2022-24035
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2022-24035
Type: osv

## Details
An issue was discovered in ONOS 2.5.1. The purge-requested intent remains on the list, but it does not respond to changes in topology (e.g., link failure). In combination with other applications, it could lead to a failure of network management.

## References
- https://wiki.onosproject.org/display/ONOS/Intent+Framework
- https://www.usenix.org/system/files/sec23fall-prepub-285_kim-jiwon.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24035.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-24035
