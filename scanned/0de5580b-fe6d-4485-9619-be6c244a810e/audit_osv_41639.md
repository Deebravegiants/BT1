# [H] CVE-2026-6272

## Summary
Severity: High
Advisory: CVE-2026-6272
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-6272
Type: osv

## Details
A client holding only a read JWT scope can still register itself as a signal provider through the production kuksa.val.v2 OpenProviderStream API by sending ProvideSignalRequest.

1. Obtain any valid token with only read scope.
2. Connect to the normal production gRPC API (kuksa.val.v2).
3. Open OpenProviderStream.
4. Send ProvideSignalRequest for a target signal ID.
5. Wait for the broker to forward GetProviderValueRequest.
6. Reply with attacker-controlled GetProviderValueResponse.
7. Other clients performing GetValue / GetValues for that signal receive forged data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6272.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6272
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/98
- https://github.com/eclipse-kuksa/kuksa-databroker
