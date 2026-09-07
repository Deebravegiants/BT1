# [M] Umbraco Vulnerable to Improper File Access and Credential Exposure in Dictionary Import Functionality

## Summary
Severity: Medium
Advisory: GHSA-hfv2-pf68-m33x
CVE: CVE-2025-66625
CWE: CWE-200, CWE-377, CWE-552
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-hfv2-pf68-m33x
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=10.0.0 <13.12.1

## Details
### Impact
Due to unsafe handling and deletion of temporary files during the dictionary upload process, an attacker with access to the backoffice can trigger predictable requests to temporary file paths. The application’s error responses (HTTP 500 when a file exists, 404 when it does not) allow the attacker to enumerate the existence of arbitrary files on the server’s filesystem. This vulnerability does not allow reading or writing file contents.

In certain configurations, incomplete clean-up of temporary upload files may additionally expose the NTLM hash of the Windows account running the Umbraco application. The direct impact of this vulnerability is therefore limited to confidentiality, which is reflected in its CVSS base score of 4.9

While the CVSS Base Score captures only the immediate effect, the practical risk varies significantly based on hosting environment and identity configuration. Umbraco Cloud sites run under low-privilege, isolated Azure App Service worker identities, which mitigates the impact of any credential exposure. In contrast, self-hosted deployments could run Umbraco using privileged local or domain accounts. If such an account’s NTLM hash is disclosed, an attacker may be able to:
- Perform NTLM relay attacks
- Crack the hash offline to recover the underlying password
- Authenticate as the compromised identity
- Access internal systems trusted by that identity
- Move laterally within the network
- Potentially escalate to full domain compromise in weakly segmented environments

These outcomes are not part of the CVSS base score, which only rates the immediate confidentiality impact, but represent realistic downstream consequences for installations using elevated or widely-trusted service accounts. Self-hosted environments running Umbraco under privileged identities are therefore at significantly higher risk.

Vulnerability found and reported by Tomasz Holeksa at Pentest Limited

### Patches
The issue has been patched in 13.12.1.

### Workarounds
The issue can only be exploited by authorized backoffice accounts with access to the "Translations" section.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-hfv2-pf68-m33x
- https://nvd.nist.gov/vuln/detail/CVE-2025-66625
- https://github.com/umbraco/Umbraco-CMS/commit/7505efd433189037f46547932d4a8b603fd4a615
- https://github.com/umbraco/Umbraco-CMS
