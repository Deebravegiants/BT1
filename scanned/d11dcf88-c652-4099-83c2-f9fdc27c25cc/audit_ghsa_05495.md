# [H] ComfyUI-Manager is Vulnerable to CRLF Injection in Configuration Handler

## Summary
Severity: High
Advisory: GHSA-562r-8445-54r2
CVE: CVE-2026-22777
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-562r-8445-54r2
Type: github-advisory

## Affected
- PyPI: `comfy-cli` — affected >=4.0.0 <4.0.5
- PyPI: `comfy-cli` — affected >=0 <3.39.2

## Details
## Impact

**Vulnerability Type**: CRLF Injection via ConfigParser

An attacker can inject special characters into HTTP query parameters to add arbitrary configuration values to the `config.ini` file. This can lead to security setting tampering or modification of application behavior.

**Affected Users**: Users running ComfyUI-Manager in environments where ComfyUI is configured with the `--listen` option to allow remote access.

**CVSS Score**: 7.5 (High)

## Patches

Fixed in the following versions:
- **3.39.2** (v3.x branch)
- **4.0.5** (v4.x branch)

Sanitization logic was added to the `write_config()` function to remove CRLF and NULL characters from all string values.

## Workarounds

If upgrading is not possible:
- Run ComfyUI-Manager only on trusted networks
- Block external access via firewall
- Run on localhost only without the `--listen` option

## References

- [CWE-93: Improper Neutralization of CRLF Sequences](https://cwe.mitre.org/data/definitions/93.html)
- [OWASP CRLF Injection](https://owasp.org/www-community/vulnerabilities/CRLF_Injection)

## Credit

This vulnerability was reported by:
- 李存义 <xiaoheihei1107@gmail.com>
- D0n9 Li <wyd0n9@gmail.com>
- Swings <swing@mail.exp.sh>
- Osword from SGLAB of Legendsec at Qi'anxin Group <zhzhdoai@gmail.com>

## References
- https://github.com/Comfy-Org/ComfyUI-Manager/security/advisories/GHSA-562r-8445-54r2
- https://nvd.nist.gov/vuln/detail/CVE-2026-22777
- https://github.com/Comfy-Org/ComfyUI-Manager/commit/ef8703a3d7ab4e6ecda8f96e0c5816c23d1cb262
- https://github.com/Comfy-Org/ComfyUI-Manager/commit/f4fa394e0f03b013f1068c96cff168ad10bd0410
- https://github.com/Comfy-Org/ComfyUI-Manager
