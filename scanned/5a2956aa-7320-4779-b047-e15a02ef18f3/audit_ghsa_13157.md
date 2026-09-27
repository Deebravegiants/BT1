# [C] NLnet Labs’ Routinator vulnerable to path traversal

## Summary
Severity: Critical
Advisory: GHSA-5rxf-fqch-7vqp
CVE: CVE-2023-39916
CWE: CWE-22, CWE-35
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-5rxf-fqch-7vqp
Type: github-advisory

## Affected
- crates.io: `routinator` — affected >=0.9.0 <0.12.2

## Details
NLnet Labs’ Routinator 0.9.0 up to and including 0.12.1 contains a possible path traversal vulnerability in the optional, off-by-default keep-rrdp-responses feature that allows users to store the content of responses received for RRDP requests. The location of these stored responses is constructed from the URL of the request. Due to insufficient sanitation of the URL, it is possible for an attacker to craft a URL that results in the response being stored outside of the directory specified for it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39916
- https://github.com/NLnetLabs/routinator/pull/892
- https://github.com/NLnetLabs/routinator
- https://github.com/NLnetLabs/routinator/releases/tag/v0.12.2
- https://nlnetlabs.nl/downloads/routinator/CVE-2023-39916.txt
