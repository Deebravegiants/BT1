# [M] Discourse subject to Allocation of Resources Without Limits or Throttling

## Summary
Severity: Medium
Advisory: BIT-discourse-2023-22739
Aliases: CVE-2023-22739, GHSA-rqgr-g6v7-jcfc
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-22739
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.0.1

## Details
Discourse is an open source platform for community discussion. Versions prior to 3.0.1 (stable), 3.1.0.beta2 (beta), and 3.1.0.beta2 (tests-passed) are subject to Allocation of Resources Without Limits or Throttling. As there is no limit on data contained in a draft, a malicious user can create an arbitrarily large draft, forcing the instance to a crawl. This issue is patched in versions 3.0.1 (stable), 3.1.0.beta2 (beta), and 3.1.0.beta2 (tests-passed). There are no workarounds.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-rqgr-g6v7-jcfc
- https://nvd.nist.gov/vuln/detail/CVE-2023-22739
