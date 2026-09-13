# [H] osctrl is Vulnerable to OS Command Injection via Environment Configuration

## Summary
Severity: High
Advisory: GHSA-rchw-322g-f7rm
CVE: CVE-2026-28279
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-rchw-322g-f7rm
Type: github-advisory

## Affected
- Go: `github.com/jmpsec/osctrl` — affected >=0 <0.5.0

## Details
### Summary
An OS command injection vulnerability exists in the `osctrl-admin` environment configuration. An authenticated administrator can inject arbitrary shell commands via the hostname parameter when creating or editing environments. These commands are embedded into enrollment one-liner scripts generated using Go's `text/template` package (which does not perform shell escaping) and execute on every endpoint that enrolls using the compromised environment.

### Impact
An attacker with administrator access can achieve remote code execution on every endpoint that enrolls using the compromised environment. Commands execute as root/SYSTEM (the privilege level used for osquery enrollment) before osquery is installed, leaving no agent-level audit trail. This enables backdoor installation, credential exfiltration, and full endpoint compromise.

### Patches
Fixed in osctrl `v0.5.0`. Users should upgrade immediately.

### Workarounds
Restrict osctrl administrator access to trusted personnel. Review existing environment configurations for suspicious hostnames. Monitor enrollment scripts for unexpected commands.

### Credits

Leon Johnson and Kwangyun Keum from TikTok USDS JV Offensive Security Operations (Offensive Privacy Team)

https://github.com/Kwangyun → @Kwangyun
https://github.com/sho-luv → @sho-luv

## References
- https://github.com/jmpsec/osctrl/security/advisories/GHSA-rchw-322g-f7rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-28279
- https://github.com/jmpsec/osctrl/pull/777
- https://github.com/jmpsec/osctrl/pull/780
- https://github.com/jmpsec/osctrl
