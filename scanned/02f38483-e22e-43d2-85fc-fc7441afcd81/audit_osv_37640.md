# [M] Sipeed NanoKVM unauthenticated Wi-Fi configuration endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-32296
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-32296
Type: osv

## Details
Sipeed NanoKVM before 2.3.1 exposes a Wi-Fi configuration endpoint without proper security checks, allowing an unauthenticated attacker with network access to change the saved configured Wi-Fi network to one of the attacker's choosing, or craft a request to exhaust the system memory and terminate the KVM process.

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-26-076-01.json
- https://www.cve.org/CVERecord?id=CVE-2026-32296
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32296.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32296
- https://github.com/sipeed/NanoKVM/blob/main/CHANGELOG.md#231-2025-12-26
- https://eclypsium.com/blog/kvm-devices-the-keys-to-your-kingdom-are-hanging-on-the-network/
