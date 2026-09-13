# [M] Renovate before 44.14.4 TLS Private Key Log Sanitisation

## Summary
Severity: Medium
Advisory: CVE-2026-88883
Aliases: GHSA-4hmw-qw74-vrhm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88883
Type: osv

## Details
Renovate is an automated dependency update tool. In versions before 44.14.4 (and Mend Renovate CE/EE images before 15.4.0 and the mend-renovate-enterprise-edition Helm chart before 10.4.0), log sanitisation for TLS private keys used for Mutual TLS was incomplete. While the value of hostRules[].httpsPrivateKey was redacted in the field itself, the same private key value was not redacted if it also appeared elsewhere — for example in another configuration option or in a log message under a key other than httpsPrivateKey — causing the full private key to be written to Renovate's logs in cleartext. This affects deployments that configure Mutual TLS through hostRules[].httpsPrivateKey without passing the value through the documented `secrets` configuration. Anyone able to read the resulting logs can recover the private key. The issue is fixed in Renovate 44.14.4, which redacts any value supplied as hostRules[].httpsPrivateKey wherever it appears in the logs; as a workaround, supply the key via the `secrets` configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88883.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-4hmw-qw74-vrhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-88883
- https://www.vulncheck.com/advisories/renovate-before-44.14.4-tls-private-key-log-sanitisation
