# [C] Argument Injection in BOSH CLI Allows Local Command Execution on Operator Workstations via Compromised Director

## Summary
Severity: Critical
Advisory: CVE-2026-47829
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-47829
Type: osv

## Details
Argument Injection in bosh-cli allows a compromised BOSH Director to inject arbitrary OpenSSH options into the locally-spawned ssh process when an operator runs bosh ssh -c, bosh logs -f, or other non-interactive SSH paths, leading to local command execution on the operator's workstation.
Affected versions: bosh-cli versions prior to v7.10.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47829.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47829
- https://www.cloudfoundry.org/blog/cve-2026-47829-argument-injection-in-bosh-cli-allows-local-command-execution-on-operator-workstations-via-compromised-director/
