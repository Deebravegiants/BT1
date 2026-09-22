# [H] FOG's authentication bypass leads to full SQL DB dump

## Summary
Severity: High
Advisory: CVE-2025-58443
Aliases: GHSA-mvwm-9m2h-87p9
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2025-09-06
Source: https://osv.dev/vulnerability/CVE-2025-58443
Type: osv

## Details
FOG is a free open-source cloning/imaging/rescue suite/inventory management system. Versions 1.5.10.1673 and below contain an authentication bypass vulnerability. It is possible for an attacker to perform an unauthenticated DB dump where they could pull a full SQL DB without credentials. A fix is expected to be released 9/15/2025. To address this vulnerability immediately, upgrade to the latest version of either the dev-branch or working-1.6 branch. This will patch the issue for users concerned about immediate exposure. See the FOG Project documentation for step-by-step upgrade instructions: https://docs.fogproject.org/en/latest/install-fog-server#choosing-a-fog-version.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58443.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-mvwm-9m2h-87p9
- https://nvd.nist.gov/vuln/detail/CVE-2025-58443
