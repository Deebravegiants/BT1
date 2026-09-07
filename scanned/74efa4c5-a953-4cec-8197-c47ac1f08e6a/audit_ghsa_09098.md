# [M] CrowdSec LAPI: Denial of Service via Unbounded Gzip Decompression

## Summary
Severity: Medium
Advisory: GHSA-273h-gvwr-c3qj
CVE: CVE-2026-44981
CWE: CWE-409
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-273h-gvwr-c3qj
Type: github-advisory

## Affected
- Go: `github.com/crowdsecurity/crowdsec` — affected >=1.7.0 <1.7.8

## Details
The LAPI router uses `gin-contrib/gzip` with `DefaultDecompressHandle` globally (`pkg/apiserver/controllers/controller.go`).
This middleware decompresses incoming request bodies without enforcing a maximum decompressed size. 

The endpoints `/v1/watchers` or `/v1/watchers/login` require no authentication.
An attacker can send small gzip-compressed JSON payloads that, when decompressed, result in hundreds of MB of valid JSON occupying server memory.
Sending enough requests concurrently will cause LAPI to allocate excessive heap memory, leading the OS to forcibly terminate the process.
 
This vulnerability is not exploitable from the network in default configurations, as LAPI only listens on the loopback interface.
If developers' applications are using a multi-server setup, LAPI will be exposed in the network, in which case they are at risk if untrusted IPs can access it.
 
### Impact

Exploiting this vulnerability will make LAPI unreachable, meaning that bouncers will not be able to fetch new decisions (but existing decisions will still be enforced) and log processors will not be able to send alerts, effectively denying the creation of new decisions.

### Workarounds

If the LAPI is exposed on the network (either directly or through a reverse proxy), for example in the case of a multi-server deployment, restrict access to trusted IP addresses.

## References
- https://github.com/crowdsecurity/crowdsec/security/advisories/GHSA-273h-gvwr-c3qj
- https://github.com/crowdsecurity/crowdsec
- https://github.com/crowdsecurity/crowdsec/releases/tag/v1.7.8
