# [M] Malicious agent may be able to impersonate another agent in GoCD

## Summary
Severity: Medium
Advisory: CVE-2022-39310
Aliases: GHSA-4fp5-33jh-hgcq
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-39310
Type: osv

## Details
GoCD is a continuous delivery server. GoCD helps you automate and streamline the build-test-release cycle for continuous delivery of your product. GoCD versions prior to 21.1.0 can allow one authenticated agent to impersonate another agent, and thus receive work packages for other agents due to broken access control and incorrect validation of agent tokens within the GoCD server. Since work packages can contain sensitive information such as credentials intended only for a given job running against a specific agent environment, this can cause accidental information disclosure. Exploitation requires knowledge of agent identifiers and ability to authenticate as an existing agent with the GoCD server. This issue is fixed in GoCD version 21.1.0. There are currently no known workarounds.

## References
- https://www.gocd.org/releases/#21-1-0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39310.json
- https://github.com/gocd/gocd/security/advisories/GHSA-4fp5-33jh-hgcq
- https://nvd.nist.gov/vuln/detail/CVE-2022-39310
- https://github.com/gocd/gocd/pull/8877
