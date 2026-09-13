# [M] Discourse chat messages should have a maximum character limit

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-41921
Aliases: CVE-2022-41921, GHSA-mfh7-6cv6-qccc
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-41921
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2.9.0

## Details
Discourse is an open-source discussion platform. Prior to version 2.9.0.beta13, users can post chat messages of an unlimited length, which can cause a denial of service for other users when posting huge amounts of text. Users should upgrade to version 2.9.0.beta13, where a limit has been introduced. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/3de765c89524a526ce611e11468d758a471a933f
- https://github.com/discourse/discourse/security/advisories/GHSA-mfh7-6cv6-qccc
- https://nvd.nist.gov/vuln/detail/CVE-2022-41921
