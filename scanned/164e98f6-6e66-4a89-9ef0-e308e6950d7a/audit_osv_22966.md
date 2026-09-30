# [M] CVE-2022-4172

## Summary
Severity: Medium
Advisory: CVE-2022-4172
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-29
Source: https://osv.dev/vulnerability/CVE-2022-4172
Type: osv

## Details
An integer overflow and buffer overflow issues were found in the ACPI Error Record Serialization Table (ERST) device of QEMU in the read_erst_record() and write_erst_record() functions. Both issues may allow the guest to overrun the host buffer allocated for the ERST memory device. A malicious guest could use these flaws to crash the QEMU process on the host.

## References
- https://lore.kernel.org/qemu-devel/20221024154233.1043347-1-lk%40c--e.de/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4172.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I7J5IRXJYLELW7D43A75LOWRUE5EU54O/
- https://nvd.nist.gov/vuln/detail/CVE-2022-4172
- https://security.netapp.com/advisory/ntap-20230127-0013/
- https://gitlab.com/qemu-project/qemu/-/issues/1268
- https://gitlab.com/qemu-project/qemu/-/commit/defb7098
