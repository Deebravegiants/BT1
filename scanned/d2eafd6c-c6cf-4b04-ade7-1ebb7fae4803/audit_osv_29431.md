# [H] Litestar repository vulnerable to Environment Variable injection in `docs-preview.yml` workflow

## Summary
Severity: High
Advisory: CVE-2024-42370
Aliases: GHSA-4hq2-rpgc-r8r7
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H)
Published: 2024-08-09
Source: https://osv.dev/vulnerability/CVE-2024-42370
Type: osv

## Details
Litestar is an Asynchronous Server Gateway Interface (ASGI) framework. In versions 2.10.0 and prior, Litestar's `docs-preview.yml` workflow is vulnerable to Environment Variable injection which may lead to secret exfiltration and repository manipulation. This issue grants a malicious actor the permission to write issues, read metadata, and write pull requests. In addition, the `DOCS_PREVIEW_DEPLOY_TOKEN` is exposed to the attacker. Commit 84d351e96aaa2a1338006d6e7221eded161f517b contains a fix for this issue.

## References
- https://github.com/litestar-org/litestar/actions/runs/10081936962/job/27875077668#step:1:17
- https://github.com/litestar-org/litestar/blob/ffaf5616b19f6f0f4128209c8b49dbcb41568aa2/.github/workflows/docs-preview.yml
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42370.json
- https://github.com/litestar-org/litestar/security/advisories/GHSA-4hq2-rpgc-r8r7
- https://nvd.nist.gov/vuln/detail/CVE-2024-42370
- https://github.com/litestar-org/litestar/commit/84d351e96aaa2a1338006d6e7221eded161f517b
