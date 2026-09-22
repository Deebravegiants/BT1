# [H] CVE-2020-5423

## Summary
Severity: High
Advisory: CVE-2020-5423
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-02
Source: https://osv.dev/vulnerability/CVE-2020-5423
Type: osv

## Details
CAPI (Cloud Controller) versions prior to 1.101.0 are vulnerable to a denial-of-service attack in which an unauthenticated malicious attacker can send specially-crafted YAML files to certain endpoints, causing the YAML parser to consume excessive CPU and RAM.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5423
