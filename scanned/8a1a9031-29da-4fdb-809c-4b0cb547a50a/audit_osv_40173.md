# [C] Yuxi has a JWT Authentication Bypass Leading to Cross-Instance Administrator Token Reuse

## Summary
Severity: Critical
Advisory: CVE-2026-50561
Aliases: GHSA-6959-99pq-c56x
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-50561
Type: osv

## Details
Yuxi is a large-model-based intelligent knowledge base and knowledge graph agent development platform. Prior to version 0.6.2, the project's authentication mechanism contains a flaw. In affected versions, the system does not sufficiently validate the identity token in the Authorization header — only performing a validity check. This allows an administrator token generated in another deployment instance or local testing environment to be used to access the backend management interfaces of a different affected instance. An attacker who obtains or constructs an acceptable administrator Authorization token may bypass normal login authentication and gain administrator privileges. This vulnerability could allow an attacker to access system configurations, invoke backend management APIs, create administrator accounts, and ultimately take over the system backend. This issue has been fixed in version 0.6.2. Before upgrading, users are advised to implement the following temporary measures: Set the environment variable `JWT_SECRET_KEY` to a non-default value, and configure a unique, sufficiently strong JWT/authentication key for each deployment instance; and/or avoid exposing backend management interfaces directly to the public network.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50561.json
- https://github.com/xerrors/Yuxi/security/advisories/GHSA-6959-99pq-c56x
- https://nvd.nist.gov/vuln/detail/CVE-2026-50561
- https://github.com/xerrors/Yuxi/issues/673
- https://github.com/xerrors/Yuxi/commit/1e8b20e30b1258d1cd3ebf3af5c6212da4b84b48
