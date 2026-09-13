# [H] Vexa's unauthenticated internal transcript endpoint exposed by default

## Summary
Severity: High
Advisory: CVE-2026-25058
Aliases: GHSA-w73r-2449-qwgh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-25058
Type: osv

## Details
Vexa is an open-source, self-hostable meeting bot API and meeting transcription API. Prior to 0.10.0-260419-1910, the Vexa transcription-collector service exposes an internal endpoint `GET /internal/transcripts/{meeting_id}` that returns transcript data for any meeting without any authentication or authorization checks. An unauthenticated attacker can enumerate all meeting IDs, access any user's meeting transcripts without credentials, and steal confidential business conversations, passwords, and/or PII. Version 0.10.0-260419-1910 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25058.json
- https://github.com/Vexa-ai/vexa/security/advisories/GHSA-w73r-2449-qwgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25058
