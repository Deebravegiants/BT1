# [C] serverless-dns is vulnerable to Command Injection through pr.yml GitHub Action Workflow

## Summary
Severity: Critical
Advisory: CVE-2025-61584
Aliases: GHSA-9g7x-737f-5xpc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-61584
Type: osv

## Details
serverless-dns is a RethinkDNS resolver that deploys to Cloudflare Workers, Deno Deploy, Fastly, and Fly.io. Versions through abd including 0.1.30 have a vulnerability where the pr.yml GitHub Action interpolates in an unsafe manner untrusted input, specifically the github.event.pull_request.head.repo.clone_url and github.head_ref, to a command in the runner. Due to the action using the pull_request_target trigger it has permissive permissions by default. An unauthorized attacker can exploit this vulnerability to push arbitrary data to the repository. The subsequent impact on the end-user is executing the attackers' code when running serverless-dns. This is fixed in commit c5537dd, and expected to be released in 0.1.31.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61584.json
- https://github.com/serverless-dns/serverless-dns/security/advisories/GHSA-9g7x-737f-5xpc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61584
- https://github.com/serverless-dns/serverless-dns/commit/c5537dd7f203c59f2b86d1e295c2371f3533946a
