# [C] CVE-2025-47151

## Summary
Severity: Critical
Advisory: CVE-2025-47151
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-47151
Type: osv

## Details
A type confusion vulnerability exists in the lasso_node_impl_init_from_xml functionality of Entr&#39;ouvert Lasso 2.5.1 and 2.8.2. A specially crafted SAML response can lead to an arbitrary code execution. An attacker can send a malformed SAML response to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2193
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2193
