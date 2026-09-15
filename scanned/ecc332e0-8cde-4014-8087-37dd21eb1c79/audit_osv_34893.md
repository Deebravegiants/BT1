# [H] AIS-catcher Integer Underflow in MQTT Packet Parsing leading to Heap Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2025-66217
Aliases: GHSA-93mj-c8q3-69rg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66217
Type: osv

## Details
AIS-catcher is a multi-platform AIS receiver. Prior to version 0.64, an integer underflow vulnerability exists in the MQTT parsing logic of AIS-catcher. This vulnerability allows an attacker to trigger a massive Heap Buffer Overflow by sending a malformed MQTT packet with a manipulated Topic Length field. This leads to an immediate Denial of Service (DoS) and, when used as a library, severe Memory Corruption that can be leveraged for Remote Code Execution (RCE). This issue has been patched in version 0.64.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66217.json
- https://github.com/jvde-github/AIS-catcher/security/advisories/GHSA-93mj-c8q3-69rg
- https://nvd.nist.gov/vuln/detail/CVE-2025-66217
- https://github.com/jvde-github/AIS-catcher/commit/e0f7242eee659909adc11a4c561c3f7011bdefe7
