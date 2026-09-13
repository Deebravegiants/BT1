# [H] CVE-2022-26061

## Summary
Severity: High
Advisory: CVE-2022-26061
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2022-26061
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the gif2h5 functionality of HDF5 Group libhdf5 1.10.4. A specially-crafted GIF file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1487
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/26xxx/CVE-2022-26061.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-26061
- https://github.com/HDFGroup/hdf5/pull/4785
