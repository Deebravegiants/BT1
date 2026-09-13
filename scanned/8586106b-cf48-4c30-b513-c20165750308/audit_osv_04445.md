# [C] Bypass of Discourse Connect using other login paths if enabled in Discourse

## Summary
Severity: Critical
Advisory: BIT-discourse-2024-49765
Aliases: CVE-2024-49765, GHSA-v8rf-pvgm-xxf2
Ecosystem: Bitnami
Published: 2024-12-23
Source: https://osv.dev/vulnerability/BIT-discourse-2024-49765
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.3

## Details
Discourse is an open source platform for community discussion. Sites that are using discourse connect but still have local logins enabled could allow attackers to bypass discourse connect to create accounts and login. This problem is patched in the latest version of Discourse. Users unable to upgrade who are using discourse connect may disable all other login methods as a workaround.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-v8rf-pvgm-xxf2
- https://nvd.nist.gov/vuln/detail/CVE-2024-49765
