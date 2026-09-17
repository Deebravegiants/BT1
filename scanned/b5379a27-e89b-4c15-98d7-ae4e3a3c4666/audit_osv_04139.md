# [C] apisix/batch-requests plugin allows overwriting the X-REAL-IP header

## Summary
Severity: Critical
Advisory: BIT-apisix-2022-24112
Aliases: CVE-2022-24112
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apisix-2022-24112
Type: osv

## Affected
- Bitnami: `apisix` — affected >=2.11.0 <2.12.1

## Details
An attacker can abuse the batch-requests plugin to send requests to bypass the IP restriction of Admin API. A default configuration of Apache APISIX (with default API key) is vulnerable to remote code execution. When the admin key was changed or the port of Admin API was changed to a port different from the data panel, the impact is lower. But there is still a risk to bypass the IP restriction of Apache APISIX's data panel. There is a check in the batch-requests plugin which overrides the client IP with its real remote IP. But due to a bug in the code, this check can be bypassed.

## References
- http://packetstormsecurity.com/files/166228/Apache-APISIX-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/166328/Apache-APISIX-2.12.1-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2022/02/11/3
- https://lists.apache.org/thread/lcdqywz8zy94mdysk7p3gfdgn51jmt94
- https://nvd.nist.gov/vuln/detail/CVE-2022-24112
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-24112
