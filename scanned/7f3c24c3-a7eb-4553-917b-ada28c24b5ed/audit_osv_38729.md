# [C] BOSH CLI Shell Injection

## Summary
Severity: Critical
Advisory: CVE-2026-41857
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-41857
Type: osv

## Details
A compromised or malicious BOSH Director can execute arbitrary shell commands on the operator's workstation when the operator runs bosh ssh (or bosh scp/bosh logs -f) with default flags.
Affected versions: BOSH CLI versions prior to 7.10.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41857.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41857
- https://www.cloudfoundry.org/blog/cve-2026-41857-bosh-cli-shell-injection/
