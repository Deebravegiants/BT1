# [C] ZeroBrew version 0.3.1 and prior Missing Checksum Verification RCE via shim.rb

## Summary
Severity: Critical
Advisory: CVE-2026-53970
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-53970
Type: osv

## Details
ZeroBrew version 0.3.1 and prior contains a missing integrity verification vulnerability in the Ruby compatibility shim that allows network attackers to execute arbitrary code by substituting malicious content at formula resource or URL-based patch URLs without checksum validation. Attackers can intercept or replace downloads for secondary resource and patch paths in shim.rb, injecting attacker-controlled build steps or source tree modifications that execute during source builds via 'zb install --build-from-source' without any integrity warning.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53970.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53970
- https://www.vulncheck.com/advisories/zerobrew-version-and-prior-missing-checksum-verification-rce-via-shim-rb
- https://github.com/lucasgelfond/zerobrew
- https://github.com/lucasgelfond/zerobrew/commit/89a60b73c7edd6b662e2a085be3d981b6ebeb1aa
