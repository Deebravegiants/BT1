# [C] Rancher cloud credentials can be used through proxy API by users without access

## Summary
Severity: Critical
Advisory: GHSA-gqf8-rvrh-g7w6
CVE: CVE-2021-25320
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-gqf8-rvrh-g7w6
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.2.0 <2.4.16
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.9

## Details
A vulnerability was discovered in Rancher 2.2.0 through the aforementioned patched versions, where cloud credentials weren't being properly validated through the Rancher API. Specifically through a proxy designed to communicate with cloud providers. Any Rancher user that was logged-in and aware of a cloud-credential ID that was valid for a given cloud provider, could call that cloud provider's API through the proxy API, and the cloud-credential would be attached. The exploit is limited to valid Rancher users. There is not a direct mitigation outside of upgrading to the patched Rancher versions.

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-gqf8-rvrh-g7w6
- https://nvd.nist.gov/vuln/detail/CVE-2021-25320
- https://bugzilla.suse.com/show_bug.cgi?id=1185514
- https://github.com/rancher/rancher
