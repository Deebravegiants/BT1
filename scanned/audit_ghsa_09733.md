# [M] mcpo-simple-server has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-3jmq-qhg3-f58j
CVE: CVE-2026-7404
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-3jmq-qhg3-f58j
Type: github-advisory

## Affected
- PyPI: `mcpo-simple-server` — affected >=0

## Details
A weakness has been identified in getsimpletool mcpo-simple-server up to 0.2.0. Affected is the function delete_shared_prompt of the file src/mcpo_simple_server/services/prompt_manager/base_manager.py. This manipulation of the argument detail causes relative path traversal. It is possible to initiate the attack remotely. The exploit has been made available to the public and could be used for attacks. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7404
- https://github.com/getsimpletool/mcpo-simple-server/issues/4
- https://github.com/getsimpletool/mcpo-simple-server
- https://vuldb.com/submit/803612
- https://vuldb.com/vuln/360140
- https://vuldb.com/vuln/360140/cti
