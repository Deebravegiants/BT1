# [H] Hard coded cryptographic key in Kiali

## Summary
Severity: High
Advisory: GHSA-64rh-r86q-75ff
CVE: CVE-2020-1764
CWE: CWE-321, CWE-798
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-64rh-r86q-75ff
Type: github-advisory

## Affected
- Go: `github.com/kiali/kiali` — affected >=0 <1.15.1

## Details
A hard-coded cryptographic key vulnerability in the default configuration file was found in Kiali, all versions prior to 1.15.1. A remote attacker could abuse this flaw by creating their own JWT signed tokens and bypass Kiali authentication mechanisms, possibly gaining privileges to view and alter the Istio configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1764
- https://github.com/kiali/kiali/commit/93f5cd0b6698e8fe8772afb8f35816f6c086aef1
- https://github.com/kiali/kiali/commit/ac7bd6c7ddb2e01356e21d360dd1c718a90706ad
- https://github.com/kiali/kiali/commit/ce48af57113c805a25179aaab1a0fac2fb93653f
- https://github.com/kiali/kiali/commit/faed1f5f90efae3df9fd6fb793f00ccc242b3a96
- https://bugzilla.redhat.com/show_bug.cgi?id=1810383
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1764
- https://github.com/jpts/cve-2020-1764-poc
- https://kiali.io/news/security-bulletins/kiali-security-001
