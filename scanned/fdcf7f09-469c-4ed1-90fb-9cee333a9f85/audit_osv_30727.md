# [H] Suricata generic detection bypass using TCP urgent support

## Summary
Severity: High
Advisory: CVE-2024-55629
Aliases: GHSA-69wr-vhwg-84h2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-55629
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to 7.0.8, TCP streams with TCP urgent data (out of band data) can lead to Suricata analyzing data differently than the applications at the TCP endpoints, leading to possible evasions. Suricata 7.0.8 includes options to allow users to configure how to handle TCP urgent data. In IPS mode, you can use a rule such as drop tcp any any -> any any (sid:1; tcp.flags:U*;) to drop all the packets with urgent flag set.

## References
- https://redmine.openinfosecfoundation.org/issues/7411
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55629.json
- https://github.com/OISF/suricata/security/advisories/GHSA-69wr-vhwg-84h2
- https://nvd.nist.gov/vuln/detail/CVE-2024-55629
- https://github.com/OISF/suricata/commit/6882bcb3e51bd3cf509fb6569cc30f48d7bb53d7
- https://github.com/OISF/suricata/commit/779f9d8ba35c3f9b5abfa327d3a4209861bd2eb8
