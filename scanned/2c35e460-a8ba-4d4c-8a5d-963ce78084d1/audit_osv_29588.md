# [H] CVE-2024-44775

## Summary
Severity: High
Advisory: CVE-2024-44775
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-44775
Type: osv

## Details
kmqtt v0.2.7 is vulnerable to Denial of Service (DoS) due to a Null Pointer Exception. A remote attacker can cause the broker to crash by sending a specially crafted MQTT CONNECT packet that triggers an unhandled null reference, leading to an immediate process termination.

## References
- https://gist.github.com/pengwGit/26fd8630392af5d8829c2e220091ac4f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44775.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44775
