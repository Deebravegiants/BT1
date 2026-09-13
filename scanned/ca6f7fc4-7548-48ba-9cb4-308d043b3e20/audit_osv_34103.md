# [M] onion-site-template tor Secrets Baked Into Image

## Summary
Severity: Medium
Advisory: CVE-2025-54872
Aliases: GHSA-mj8m-c8w9-rw55
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54872
Type: osv

## Details
onion-site-template is a complete, scalable tor hidden service self-hosting sample. Versions which include commit 3196bd89 contain a baked-in tor image if the secrets were copied from an existing onion domain. A website could be compromised if a user shared the baked-in image, or if someone were able to acquire access to the user's device outside of a containerized environment. This is fixed by commit bc9ba0fd.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54872.json
- https://github.com/Vessel9817/onion-site-template/security/advisories/GHSA-mj8m-c8w9-rw55
- https://nvd.nist.gov/vuln/detail/CVE-2025-54872
- https://github.com/Vessel9817/onion-site-template/commit/bc9ba0fd8cc7fbb3abc6759b351885a4501bce84
