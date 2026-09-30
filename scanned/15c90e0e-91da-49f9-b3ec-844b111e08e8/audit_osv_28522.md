# [H] CVE-2024-34050

## Summary
Severity: High
Advisory: CVE-2024-34050
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-29
Source: https://osv.dev/vulnerability/CVE-2024-34050
Type: osv

## Details
Open Networking Foundation SD-RAN Rimedo rimedo-ts 0.1.1 has a slice bounds out-of-range panic in "return uint64(b[2])<<16 | uint64(b[1])<<8 | uint64(b[0])" in reader.go.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34050.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34050
- https://github.com/onosproject/rimedo-ts/issues/16
