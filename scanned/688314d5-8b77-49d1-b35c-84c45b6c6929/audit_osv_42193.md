# [M] Trezor Safe improper security check in on-device display

## Summary
Severity: Medium
Advisory: CVE-2026-65058
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-65058
Type: osv

## Details
Trezor Safe 3, Safe 5, and Safe 7 firmware contains a confirmation-binding flaw in the Ethereum sign_tx / sign_tx_eip1559 flow. For contract interactions, the device confirms only the initial calldata chunk while the signature commits to the full streamed calldata. An attacker could present calldata to a victim then supply a different tail that changes the signed transaction. Fixed in 70c9b0c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65058.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65058
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2026/va-26-202-02.json
- https://www.cve.org/CVERecord?id=CVE-2026-65058
- https://github.com/trezor/trezor-firmware/commit/70c9b0c07748
