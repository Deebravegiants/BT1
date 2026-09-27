# [C] CVE-2021-31856

## Summary
Severity: Critical
Advisory: CVE-2021-31856
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-28
Source: https://osv.dev/vulnerability/CVE-2021-31856
Type: osv

## Details
A SQL Injection vulnerability in the REST API in Layer5 Meshery 0.5.2 allows an attacker to execute arbitrary SQL commands via the /experimental/patternfiles endpoint (order parameter in GetMesheryPatterns in models/meshery_pattern_persister.go).

## References
- https://meshery.io
- https://github.com/layer5io/meshery/pull/2745
