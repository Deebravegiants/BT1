# [H] Discourse leaks private topic title and post excerpt via user action API endpoint

## Summary
Severity: High
Advisory: BIT-discourse-2026-27934
Aliases: CVE-2026-27934, GHSA-824f-66wh-xx3g
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27934
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Versions prior to 2026.3.0, 2026.2.1, and 2026.1.2 have a lack of visibility checks with a user action API endpoint that results in disclosure of the title and post excerpt to unauthorized users, leading to information disclosure. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-824f-66wh-xx3g
- https://nvd.nist.gov/vuln/detail/CVE-2026-27934
