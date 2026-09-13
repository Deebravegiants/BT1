# [H] Synapse allows unsupported content types to lead to memory exhaustion

## Summary
Severity: High
Advisory: GHSA-rfq8-j7rh-8hf2
CVE: CVE-2024-52805
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-rfq8-j7rh-8hf2
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.120.1

## Details
### Impact

In Synapse before 1.120.1, `multipart/form-data` requests can in certain configurations transiently increase memory consumption beyond expected levels while processing the request, which can be used to amplify denial of service attacks.

### Patches

Synapse 1.120.1 resolves the issue by denying requests with unsupported `multipart/form-data` content type.

### Workarounds

Limiting request sizes or blocking the `multipart/form-data` content type before the requests reach Synapse, for example in a reverse proxy, alleviates the issue. Another approach that mitigates the attack is to use a low `max_upload_size` in Synapse.

### References

- https://github.com/twisted/twisted/issues/4688#issuecomment-1167705518
- https://github.com/twisted/twisted/issues/4688#issuecomment-2385711609

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-rfq8-j7rh-8hf2
- https://nvd.nist.gov/vuln/detail/CVE-2024-52805
- https://github.com/twisted/twisted/issues/4688#issuecomment-1167705518
- https://github.com/twisted/twisted/issues/4688#issuecomment-2385711609
- https://github.com/element-hq/synapse
