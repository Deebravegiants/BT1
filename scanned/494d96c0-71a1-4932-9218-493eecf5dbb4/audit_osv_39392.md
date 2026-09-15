# [H] Microsoft APM: Symlinks under `.apm/prompts/` and `.apm/agents/` are dereferenced during `apm install`, copying host-local file contents into the project tree

## Summary
Severity: High
Advisory: CVE-2026-45539
Aliases: GHSA-q5pp-gvjg-h7v4, PYSEC-2026-2377
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45539
Type: osv

## Details
Microsoft APM is an open-source, community-driven dependency manager for AI agents. From 0.5.4 to 0.12.4, two primitive integrators in apm-cli enumerate package files with bare Path.glob() / Path.rglob() calls and read each match with Path.read_text(), transparently following symbolic links. A symlink committed inside a remote APM dependency under .apm/prompts/<x>.prompt.md or .apm/agents/<x>.agent.md is preserved verbatim into apm_modules/ on clone and then dereferenced during integration, with the resolved content written as a regular file into the project's deploy directories. The package content_hash, the pre-deploy SecurityGate scan, and apm audit do not flag this. The deploy roots are not added to the auto-generated .gitignore, so the resulting files are staged by git add by default. This vulnerability is fixed in 0.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45539.json
- https://github.com/microsoft/apm/security/advisories/GHSA-q5pp-gvjg-h7v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45539
