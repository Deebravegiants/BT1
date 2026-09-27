# [M] hermes's raw options logging may disclose secrets passed in via subcommand options argument

## Summary
Severity: Medium
Advisory: GHSA-jm5j-jfrm-hm23
CVE: CVE-2026-22798
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-jm5j-jfrm-hm23
Type: github-advisory

## Affected
- PyPI: `hermes` — affected >=0.8.1 <0.9.1

## Details
Thanks, @thunze for reporting this!

`hermes` subcommands take arbitrary options under the `-O` argument. These have been logged in raw form since https://github.com/softwarepub/hermes/commit/7f64f102e916c76dc44404b77ab2a80f5a4e59b1 in: https://github.com/softwarepub/hermes/blob/3a92f42b2b976fdbc2c49a621de6d665364a7cee/src/hermes/commands/cli.py#L66

If users provide sensitive data such as API tokens (e.g., via `hermes deposit -O invenio_rdm.auth_token SECRET`), these are written to the log file in plain text, making them available to whoever can access the log file.

### Impact

As currently, `hermes.log` is not yet uploaded automatically as an artifact in CI, this vuln impacts:

- local users working on shared access computers, where logs may be written to a commonly accessible file system
- CI users whose CI logs are accessible to others, e.g., through group or organization rights

Potentially, if the changes merged from https://github.com/softwarepub/ci-templates/pull/13 are merged into `ci-templates` via https://github.com/softwarepub/ci-templates/pull/14, this would automate the disclosure of Invenio auth tokens at least for all CI runs against Invenio instances!

### Patches

This has been patched in [`hermes` 0.9.1](TODO) by masking all values passed using `-O`.

### Workarounds

Upgrade to `hermes` >= 0.9.1.

## References
- https://github.com/softwarepub/hermes/security/advisories/GHSA-jm5j-jfrm-hm23
- https://nvd.nist.gov/vuln/detail/CVE-2026-22798
- https://github.com/softwarepub/hermes/commit/7f64f102e916c76dc44404b77ab2a80f5a4e59b1
- https://github.com/softwarepub/hermes/commit/90cb86acd026e7841f2539ae7a1b284a7f263514
- https://github.com/softwarepub/hermes
