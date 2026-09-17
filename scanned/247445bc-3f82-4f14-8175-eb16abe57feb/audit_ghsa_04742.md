# [H] Docker MCP Gateway: Argument injection via OCI image label YAML

## Summary
Severity: High
Advisory: GHSA-r2xf-7jw5-pjg6
CVE: CVE-2026-55887
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-r2xf-7jw5-pjg6
Type: github-advisory

## Affected
- Go: `github.com/docker/mcp-gateway` — affected >=0.21.0 <0.42.2

## Details
## Summary

A maliciously crafted OCI image label can inject arbitrary arguments into the `docker run` command line constructed by the MCP Gateway. An attacker who controls an image that the victim references via `docker://`, or that the victim's catalog pulls a snapshot from, can mount the host filesystem, run as UID 0, and execute arbitrary code on the host.
  
## Details

 The `io.docker.server.metadata` OCI image label is YAML-unmarshalled directly into the wide `catalog.Server` struct, which carries runtime-shaping fields (`Volumes`, `User`, `Command`, `ExtraHosts`, `AllowHosts`, `DisableNetwork`, `Env`, `Remote`, `SSEEndpoint`, `OAuth`,`Secrets`, `LongLived`, `Policy`) alongside descriptive fields. Every runtime field carries a YAML tag, so the unmarshal mass-assigns from the attacker-controlled label content; only `Image` is overwritten afterwards. The gateway's container-launch code then appends those fields verbatim as `docker run` flags (`-v`, `-u`, `--add-host`) with no allowlist or origin check, and execs `docker` with the resulting argv.

## Impact
  
A malicious image author can achieve arbitrary code execution as UID 0 on the host of a victim running an affected version of MCP Gateway. Attacker-injected `-v /:/host`, `-u root`, and `-v /var/run/docker.sock:/var/run/docker.sock` arguments reach the `docker run` invocation that launches the MCP server container, giving the attacker full host filesystem access and root execution. The container/host trust boundary is bypassed at container-creation time, so the `--security-opt no-new-privileges` flag the gateway applies provides no protection: no in-container privilege escalation is needed.

## Patches
The OCI image-label parser now only populates descriptive fields from the image label, which excludes fields that control the container runtime.

## Credit

This issue was reported by Jabr Al-Otaibi `@ DarkCov` working with TrendAI Zero Day Initiative

## References
- https://github.com/docker/mcp-gateway/security/advisories/GHSA-r2xf-7jw5-pjg6
- https://github.com/docker/mcp-gateway
