# [M] Instance config inline secret exposure in Grafana

## Summary
Severity: Medium
Advisory: GHSA-9c4x-5hgq-q3wh
CVE: CVE-2021-41090
CWE: CWE-200, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-08
Source: https://github.com/advisories/GHSA-9c4x-5hgq-q3wh
Type: github-advisory

## Affected
- Go: `github.com/grafana/agent` — affected >=0.14.0 <0.21.2

## Details
### Impact
Some inline secrets are exposed in plaintext over the Grafana Agent HTTP server:

* Inline secrets for metrics instance configs in the base YAML file are exposed at `/-/config` 
* Inline secrets for integrations are exposed at `/-/config`
* Inline secrets for Consul ACL tokens and ETCD basic auth when configured for the scraping service at `/-/config`.
* Inline secrets for the Kafka receiver for OpenTelemetry-Collector tracing at `/-/config`.
* Inline secrets for metrics instance configs loaded from the scraping service are exposed at `/agent/api/v1/configs/{name}`.

Inline secrets will be exposed to anyone being able to reach these endpoints.

Secrets found in these sections are used for:

* Delivering metrics to a Prometheus Remote Write system 
* Authenticating against a system for discovering Prometheus targets 
* Authenticating against a system for collecting metrics (scrape_configs and integrations)
* Authenticating against a Consul or ETCD for storing configurations to distribute in scraping service mode 
* Authenticating against Kafka for receiving traces

Non-inlined secrets, such as `*_file`-based secrets, are not impacted by this vulnerability. 

### Patches

Download [v0.20.1](https://github.com/grafana/agent/releases/tag/v0.20.1) or any version past [v0.21.2](https://github.com/grafana/agent/releases/tag/v0.21.2) to patch Grafana Agent. These patches obfuscate the listed impacted secrets from the vulnerable endpoints.

The patches also disable the endpoints by default. Pass the command-line flag `--config.enable-read-api` to opt-in and re-enable the endpoints.  
 
### Workarounds
If for some reason you cannot upgrade, use non-inline secrets where possible. Not all configuration options may have a non-inline equivalent.

You also may desire to restrict API access to Grafana Agent, with some combination of:

* Restrict network interfaces Grafana Agent listens on through `http_listen_address` in the `server` block. `127.0.0.1` is the most restrictive, `0.0.0.0` is the default. 
* Configure Grafana Agent to use HTTPS with client authentication. 
* Use firewall rules to restrict external access to Grafana Agent's API.

## References
- https://github.com/grafana/agent/security/advisories/GHSA-9c4x-5hgq-q3wh
- https://nvd.nist.gov/vuln/detail/CVE-2021-41090
- https://github.com/grafana/agent/pull/1152
- https://github.com/grafana/agent/commit/a5479755e946e5c7cddb793ee9adda8f5692ba11
- https://github.com/grafana/agent/commit/af7fb01e31fe2d389e5f1c36b399ddc46b412b21
- https://github.com/grafana/agent
- https://github.com/grafana/agent/releases/tag/v0.20.1
- https://github.com/grafana/agent/releases/tag/v0.21.2
- https://security.netapp.com/advisory/ntap-20211229-0004
