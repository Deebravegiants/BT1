# [M] Free5GC AMF is vulnerable to DoS through its HandleRegistrationComplete function

## Summary
Severity: Medium
Advisory: GHSA-xq44-64rg-8g3h
CVE: CVE-2026-4531
CWE: CWE-404
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-22
Source: https://github.com/advisories/GHSA-xq44-64rg-8g3h
Type: github-advisory

## Affected
- Go: `github.com/free5gc/amf` — affected >=0 <1.4.3-0.20260306074636-52e9386401ce

## Details
A weakness has been identified in Free5GC 4.1.0. Affected is the function HandleRegistrationComplete of the file internal/gmm/handler.go of the component AMF. Executing a manipulation can lead to denial of service. The attack may be performed from remote. This patch is called 52e9386401ce56ea773c5aa587d4cdf7d53da799. It is best practice to apply a patch to resolve this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4531
- https://github.com/free5gc/free5gc/issues/792
- https://github.com/free5gc/amf/pull/198
- https://github.com/free5gc/amf/commit/52e9386401ce56ea773c5aa587d4cdf7d53da799
- https://github.com/free5gc/amf
- https://vuldb.com/?ctiid.352319
- https://vuldb.com/?id.352319
- https://vuldb.com/?submit.774073
