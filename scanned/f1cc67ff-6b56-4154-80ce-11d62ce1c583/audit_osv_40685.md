# [H] TLS Certificate Verification Disabled on CXF Transport Clients in epa4all

## Summary
Severity: High
Advisory: CVE-2026-54342
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-54342
Type: osv

## Details
In epa4all, prior to version 2026-05-20, an attacker on the network path between epa4all and any backend (ePA Aktensystem, Konnektor, IDP, TSS) can present a self-signed TLS certificate and intercept the connection. For non-VAU connections (Konnektor, IDP), this allows direct read and modification of the inner traffic, including smartcard operations and OIDC authentication exchanges. For the ePA backend, the disabled TLS verification is the transport-level enabler for the VAU MITM described in GHSA-vvh7-x6c7-46gh. This issue has been patched in version 2026-05-20.

## References
- https://github.com/med-united/epa4all/releases/tag/2026-05-20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54342.json
- https://github.com/med-united/epa4all/security/advisories/GHSA-296w-v8f6-3rf7
- https://github.com/med-united/epa4all/security/advisories/GHSA-vvh7-x6c7-46gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-54342
- https://www.machinespirits.com/advisory/b98b02
