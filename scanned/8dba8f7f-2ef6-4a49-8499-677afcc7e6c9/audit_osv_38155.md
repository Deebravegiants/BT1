# [C] Aperi'Solve Affected by Unauthenticated RCE via JPSeek Analyzer Command

## Summary
Severity: Critical
Advisory: CVE-2026-34977
Aliases: GHSA-8r22-62p7-9jrp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-34977
Type: osv

## Details
Aperi'Solve is an open-source steganalysis web platform. In versions 3.1.3 through 3.2.0, when uploading a JPEG, a user can specify an optional password to accompany the JPEG. This password is then directly passed into an expect command, which is then subsequently passed into a bash -c command, without any form of sanitization or validation. An unauthenticated attacker can achieve root-level RCE inside the worker container with a single HTTP request, enabling full read/write access to all user-uploaded images, analysis results, and plaintext steganography passwords stored on disk. Because the container shares a Docker network with PostgreSQL and Redis (no authentication on either), the attacker can pivot to dump the entire database or manipulate the job queue to poison results for other users. If Docker socket mounting or host volume mounts are present, this could escalate to full host compromise. This would also include defacement of the website itself. This vulnerability is fixed in 3.2.1.

## References
- https://github.com/Zeecka/AperiSolve/blob/9fc388c629f86221bf2a265559eba5650d39fc29/aperisolve/analyzers/jpseek.py
- https://github.com/Zeecka/AperiSolve/releases/tag/3.1.3
- https://github.com/Zeecka/AperiSolve/releases/tag/3.2.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34977.json
- https://github.com/Zeecka/AperiSolve/security/advisories/GHSA-8r22-62p7-9jrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34977
- https://github.com/Zeecka/AperiSolve/commit/0193ca4a7d8ae9d6ba6cde82d37a6f94953463b4
- https://github.com/Zeecka/AperiSolve/pull/173
- https://github.com/Zeecka/AperiSolve/pull/195
