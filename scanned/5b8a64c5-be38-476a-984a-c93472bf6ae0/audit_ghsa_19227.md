# [C] goshs route not protected, allows command execution

## Summary
Severity: Critical
Advisory: GHSA-rwj2-w85g-5cmm
CVE: CVE-2025-46816
CWE: CWE-284, CWE-77
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-rwj2-w85g-5cmm
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs` — affected >=0.3.4 <1.0.5

## Details
### Summary

It seems that when running **goshs** without arguments it is possible for anyone to execute commands on the server. This was tested on version **1.0.4** of **goshs**. The command function was introduced in version **0.3.4**.

### Details

It seems that the function ```dispatchReadPump``` does not checks the option cli ```-c```, thus allowing anyone to execute arbitrary command through the use of websockets.

### PoC

Used **websocat** for the POC:
```bash
echo -e '{"type": "command", "content": "id"}' |./websocat 'ws://192.168.1.11:8000/?ws' -t
```

### Impact

The vulnerability will only impacts goshs server on vulnerable versions.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-rwj2-w85g-5cmm
- https://nvd.nist.gov/vuln/detail/CVE-2025-46816
- https://github.com/patrickhener/goshs/commit/160220974576afe5111485b8d12fd36058984cfa
- https://github.com/patrickhener/goshs
