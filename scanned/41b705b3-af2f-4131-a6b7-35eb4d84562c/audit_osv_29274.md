# [H] CVE-2024-41147

## Summary
Severity: High
Advisory: CVE-2024-41147
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2024-41147
Type: osv

## Details
An out-of-bounds write vulnerability exists in the ma_dr_flac__decode_samples__lpc functionality of Miniaudio miniaudio v0.11.21. A specially crafted .flac file can lead to memory corruption. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-2063
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-2063
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41147.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41147
