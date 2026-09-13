# [H] DigitalOcean Droplet Agent: Command Injection via Metadata Service Endpoint

## Summary
Severity: High
Advisory: GHSA-fh3m-562m-w4f6
CVE: CVE-2026-24516
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-fh3m-562m-w4f6
Type: github-advisory

## Affected
- Go: `github.com/digitalocean/droplet-agent` — affected >=0

## Details
A command injection vulnerability exists in DigitalOcean Droplet Agent through 1.3.2. The troubleshooting actioner component (internal/troubleshooting/actioner/actioner.go) processes metadata from the metadata service endpoint and executes commands specified in the TroubleshootingAgent.Requesting array without adequate input validation. While the code validates that artifacts exist in the validInvestigationArtifacts map, it fails to sanitize the actual command content after the "command:" prefix. This allows an attacker who can control metadata responses to inject and execute arbitrary OS commands with root privileges. The attack is triggered by sending a TCP packet with specific sequence numbers to the SSH port, which causes the agent to fetch metadata from http://169.254.169.254/metadata/v1.json. 

The vulnerability affects the command execution flow in internal/troubleshooting/actioner/actioner.go (insufficient validation), internal/troubleshooting/command/exec.go (direct exec.CommandContext call), and internal/troubleshooting/command/command.go (command parsing without sanitization). This can lead to complete system compromise, data exfiltration, privilege escalation, and potential lateral movement across cloud infrastructure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24516
- https://github.com/digitalocean/droplet-agent
- https://github.com/digitalocean/droplet-agent/blob/main/internal/troubleshooting/actioner/actioner.go
- https://github.com/digitalocean/droplet-agent/blob/main/internal/troubleshooting/command/command.go
- https://github.com/digitalocean/droplet-agent/blob/main/internal/troubleshooting/command/exec.go
- https://github.com/poxsky/CVE-2026-24516-DigitalOcean-RCE
