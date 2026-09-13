# [H] CVE-2025-46784

## Summary
Severity: High
Advisory: CVE-2025-46784
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-46784
Type: osv

## Details
A denial of service vulnerability exists in the lasso_node_init_from_message_with_format functionality of Entr&#39;ouvert Lasso 2.5.1. A specially crafted SAML response can lead to a memory depletion, resulting in denial of service. An attacker can send a malformed SAML response to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2195
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2195
