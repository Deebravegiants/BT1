# [H] Greenshot — Insecure .NET deserialization via WM_COPYDATA enables local code execution

## Summary
Severity: High
Advisory: CVE-2025-59050
Aliases: GHSA-8f7f-x7ww-xx5w
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-59050
Type: osv

## Details
Greenshot is an open source Windows screenshot utility. Greenshot 1.3.300 and earlier deserializes attacker-controlled data received in a WM_COPYDATA message using BinaryFormatter.Deserialize without prior validation or authentication, allowing a local process at the same integrity level to trigger arbitrary code execution inside the Greenshot process. The vulnerable logic resides in a WinForms WndProc handler for WM_COPYDATA (message 74) that copies the supplied bytes into a MemoryStream and invokes BinaryFormatter.Deserialize, and only afterward checks whether the specified channel is authorized. Because the authorization check occurs after deserialization, any gadget chain embedded in the serialized payload executes regardless of channel membership. A local attacker who can send WM_COPYDATA to the Greenshot main window can achieve in-process code execution, which may aid evasion of application control policies by running payloads within the trusted, signed Greenshot.exe process. This issue is fixed in version 1.3.301. No known workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59050.json
- https://github.com/greenshot/greenshot/security/advisories/GHSA-8f7f-x7ww-xx5w
- https://nvd.nist.gov/vuln/detail/CVE-2025-59050
- https://github.com/greenshot/greenshot/commit/f5a29a2ed3b0eb49231c0f4618300f488cf1b04d
