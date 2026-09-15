# [M] JetKVM insufficient firmware verification

## Summary
Severity: Medium
Advisory: CVE-2026-32294
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-32294
Type: osv

## Details
JetKVM prior to 0.5.4 does not verify the authenticity of downloaded firmware files. An attacker-in-the-middle or a compromised update server could modify the firmware and the corresponding SHA256 hash to pass verification.

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-26-076-01.json
- https://www.cve.org/CVERecord?id=CVE-2026-32294
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32294.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32294
- https://github.com/jetkvm/kvm/releases/tag/release%2F0.5.4
- https://eclypsium.com/blog/kvm-devices-the-keys-to-your-kingdom-are-hanging-on-the-network/
