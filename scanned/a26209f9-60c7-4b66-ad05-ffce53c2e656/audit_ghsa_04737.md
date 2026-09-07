# [H] EverOS: Path traversal in EverOS /api/v1/memory/add via unvalidated sender_id

## Summary
Severity: High
Advisory: GHSA-c795-2g9c-j48m
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c795-2g9c-j48m
Type: github-advisory

## Affected
- PyPI: `everos` — affected >=0 <1.0.1

## Details
EverOS versions 1.0.0 and earlier are vulnerable to path traversal in the POST /api/v1/memory/add ingestion endpoint. The per-message sender_id field was not validated as a path-safe identifier (unlike app_id / project_id, which already enforced this). During user-memory extraction, sender_id is used as the owner_id and joined into the filesystem path where the extracted episode is persisted as a Markdown file. A sender_id containing ../ sequences could direct the write outside the configured memory root, allowing an unauthenticated caller to create or overwrite .md files at locations writable by the server process (unauthorized arbitrary file write). The file content is partially attacker-influenced.

**Patch**:  Fixed in v1.0.1 with (1) path-safe validation on sender_id (character whitelist plus rejection of the . and .. tokens) and (2) a defense-in-depth containment check in the Markdown writer that rejects any write resolving outside the memory root before any filesystem access, covering both the write and the append read-modify-write paths.

**Remediation**:  Upgrade to EverOS 1.0.1. There is no workaround for affected versions other than upgrading.

## References
- https://github.com/EverMind-AI/EverOS/security/advisories/GHSA-c795-2g9c-j48m
- https://github.com/EverMind-AI/EverOS
- https://github.com/EverMind-AI/EverOS/releases/tag/v1.0.1
