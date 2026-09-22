# [H] BIT-node-2022-32223

## Summary
Severity: High
Advisory: BIT-node-2022-32223
Aliases: BIT-node-min-2022-32223, CVE-2022-32223
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2022-32223
Type: osv

## Affected
- Bitnami: `node` — affected >=18.0.0 <18.0.5

## Details
Node.js is vulnerable to Hijack Execution Flow: DLL Hijacking under certain conditions on Windows platforms.This vulnerability can be exploited if the victim has the following dependencies on a Windows machine:* OpenSSL has been installed and “C:\Program Files\Common Files\SSL\openssl.cnf” exists.Whenever the above conditions are present, `node.exe` will search for `providers.dll` in the current user directory.After that, `node.exe` will try to search for `providers.dll` by the DLL Search Order in Windows.It is possible for an attacker to place the malicious file `providers.dll` under a variety of paths and exploit this vulnerability.

## References
- https://hackerone.com/reports/1447455
- https://nodejs.org/en/blog/vulnerability/july-2022-security-releases/
- https://security.netapp.com/advisory/ntap-20220915-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32223
