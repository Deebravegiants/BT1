# [M] esaml XXE vulnerability allows local file disclosure and SSRF via crafted SAML messages

## Summary
Severity: Medium
Advisory: GHSA-4g2h-vm7x-747c
CVE: CVE-2026-28809
CWE: CWE-611
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-4g2h-vm7x-747c
Type: github-advisory

## Affected
- Hex: `esaml` — affected >=0

## Details
XML External Entity (XXE) vulnerability in esaml (and its forks) allows an attacker to cause the system to read local files and incorporate their contents into processed SAML documents, and potentially perform SSRF via crafted SAML messages.

esaml parses attacker-controlled SAML messages using xmerl_scan:string/2 before signature verification without disabling XML entity expansion. On Erlang/OTP versions before 27, Xmerl allows entities by default, enabling pre-signature XXE attacks. An attacker can cause the host to read local files (e.g., Kubernetes-mounted secrets) into the SAML document. If the attacker is not a trusted SAML SP, signature verification will fail and the document is discarded, but file contents may still be exposed through logs or error messages.

This issue affects all versions of esaml, including forks by arekinath, handnot2, and dropbox. Users running on Erlang/OTP 27 or later are not affected due to Xmerl defaulting to entities disabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28809
- https://github.com/Jump-App/esaml/commit/bab85efde7c136911402a881ca55173759467a26
- https://cna.erlef.org/cves/CVE-2026-28809.html
- https://github.com/arekinath/esaml
- https://osv.dev/vulnerability/EEF-CVE-2026-28809
