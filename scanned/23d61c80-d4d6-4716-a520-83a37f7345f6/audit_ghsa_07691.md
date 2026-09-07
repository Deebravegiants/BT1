# [H] fog-kubevirt allows remote attacker to perform MITM attack due to disabled certificate validation

## Summary
Severity: High
Advisory: GHSA-m3hq-3qj8-c5fm
CVE: CVE-2026-1530
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-m3hq-3qj8-c5fm
Type: github-advisory

## Affected
- RubyGems: `fog-kubevirt` — affected >=0 <1.5.1

## Details
A flaw was found in fog-kubevirt. This vulnerability allows a remote attacker to perform a Man-in-the-Middle (MITM) attack due to disabled certificate validation. This enables the attacker to intercept and potentially alter sensitive communications between Satellite and OpenShift, resulting in information disclosure and data integrity compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1530
- https://github.com/fog/fog-kubevirt/pull/168
- https://github.com/fog/fog-kubevirt/commit/8371e9ded99f9ec3e74caf2f283836109763e450
- https://github.com/fog/fog-kubevirt/commit/9603d79a239a0f68bedfc679cd1b65fbf6ec4753
- https://access.redhat.com/errata/RHSA-2026:5970
- https://access.redhat.com/errata/RHSA-2026:5971
- https://access.redhat.com/security/cve/CVE-2026-1530
- https://bugzilla.redhat.com/show_bug.cgi?id=2433784
- https://github.com/fog/fog-kubevirt
- https://github.com/fog/fog-kubevirt/blob/8adb03e07972d6e19a7713ecf2a827aa2cfe4b9e/CHANGELOG.md?plain=1#L11
- https://github.com/fog/fog-kubevirt/releases/tag/v1.5.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fog-kubevirt/CVE-2026-1530.yml
