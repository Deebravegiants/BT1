# [C] Missing TLS Certificate Verification in BOSH CLI Allows Root Code Execution via Man-in-the-Middle Credential Replay

## Summary
Severity: Critical
Advisory: CVE-2026-47828
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-47828
Type: osv

## Details
During bosh create-env and bosh delete-env, the CLI uploads compiled CPI packages and rendered job templates to the new VM's DAV blobstore over HTTPS without verifying the server certificate, even though a CA certificate for that endpoint is available in the installation manifest. A network attacker can terminate the TLS connection, harvest the Basic-auth credentials, and read the rendered-templates archive containing every bootstrap secret for the new BOSH Director, then replay the credentials against the real VM's agent for root code execution.
Affected versions: bosh-cli versions prior to v7.10.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47828.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47828
- https://www.cloudfoundry.org/blog/cve-2026-47828-missing-tls-certificate-verification-in-bosh-cli-allows-root-code-execution-via-man-in-the-middle-credential-replay/
