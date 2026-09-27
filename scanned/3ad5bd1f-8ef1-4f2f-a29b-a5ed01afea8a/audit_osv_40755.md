# [H] Kestra BasicAuth Password Stored as SHA-512 Enables Offline Brute-Force Attack

## Summary
Severity: High
Advisory: CVE-2026-55069
Aliases: GHSA-m727-pcjm-j28h
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-55069
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to 1.3.24, this vulnerability exists in the BasicAuth authentication component of the Kestra OSS workflow orchestration platform. An attacker who gains read access to the PostgreSQL database can exploit SHA-512's high computation speed to recover the administrator password offline. In Kubernetes deployments, a successful crack further enables reading of the cluster ServiceAccount Token and all K8s Secrets, achieving vertical privilege escalation. This vulnerability is fixed in 1.3.24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55069.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-m727-pcjm-j28h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55069
