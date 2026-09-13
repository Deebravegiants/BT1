# [M] Envoy Gateway Log Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mf24-chxh-hmvj
CVE: CVE-2025-25294
CWE: CWE-117
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-06
Source: https://github.com/advisories/GHSA-mf24-chxh-hmvj
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.2.7
- Go: `github.com/envoyproxy/gateway` — affected >=1.3.0-rc.1 <1.3.1

## Details
### Impact
In all Envoy Gateway versions prior to 1.2.7 and 1.3.1 a default Envoy Proxy access log configuration is used. This format is vulnerable to log injection attacks. 

If the attacker uses a specially crafted user-agent which performs json injection, then he could add and overwrite fields to the access log. 

Examples of attacks include:

-  Using following string as user agent : `HELLO-WORLD", "evil-ip": "1.1.1.1", "x-forwarded-for": "1.1.1.1` would lead to setting of new access log properties and overwrite of existing properties. Existing properties such as the value of the X-Forwarded-For header may have importance for security analysis of access logs, and their overwrite can be used to hide malicious activity. 

- Using the following string as user-agent : `"` which renders an invalid json document. The invalid document may fail to be processed by observability solutions, which would allow attacker to hide malicious activity.  

### Patches
1.3.1, 1.2.7

### Fix
Using JSON format as the default format for access logs. The logged document will contain the same key and values as before. Only the order of properties is different inside the logged document.

### Workaround
One can overwrite the old text based default format with JSON formatter by setting the following property: 
"EnvoyProxy.spec.telemetry.[accessLog](https://gateway.envoyproxy.io/v1.3/api/extension_types/#proxyaccesslog)" to 

```
settings:
- format:
    type: JSON
    json:
      start_time: '%START_TIME%'
      method: '%REQ(:METHOD)%'
      x-envoy-origin-path: '%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%'
      protocol: '%PROTOCOL%'
      response_code: '%RESPONSE_CODE%'
      response_flags: '%RESPONSE_FLAGS%'
      response_code_details: '%RESPONSE_CODE_DETAILS%'
      connection_termination_details: '%CONNECTION_TERMINATION_DETAILS%'
      upstream_transport_failure_reason: '%UPSTREAM_TRANSPORT_FAILURE_REASON%'
      bytes_received: '%BYTES_RECEIVED%'
      bytes_sent: '%BYTES_SENT%'
      duration: '%DURATION%'
      x-envoy-upstream-service-time: '%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%'
      x-forwarded-for: '%REQ(X-FORWARDED-FOR)%'
      user-agent: '%REQ(USER-AGENT)%'
      x-request-id: '%REQ(X-REQUEST-ID)%'
      :authority: '%REQ(:AUTHORITY)%'
      upstream_host: '%UPSTREAM_HOST%'
      upstream_cluster: '%UPSTREAM_CLUSTER%'
      upstream_local_address: '%UPSTREAM_LOCAL_ADDRESS%'
      downstream_local_address: '%DOWNSTREAM_LOCAL_ADDRESS%'
      downstream_remote_address: '%DOWNSTREAM_REMOTE_ADDRESS%'
      requested_server_name: '%REQUESTED_SERVER_NAME%'
      route_name: '%ROUTE_NAME%'
```
see API definition [here](https://gateway.envoyproxy.io/v1.3/api/extension_types/#proxyaccesslogformat)

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-mf24-chxh-hmvj
- https://nvd.nist.gov/vuln/detail/CVE-2025-25294
- https://github.com/envoyproxy/gateway/commit/041d474a70d5921e5d65e6e14ea60e14dac70b01
- https://github.com/envoyproxy/gateway/commit/358bed50dcb7b32f39a2edb252fb1399c7fc65dc
- https://github.com/envoyproxy/gateway/commit/8f48f5199cf1bbb9a8ac0695c5171bfef6c9198a
- https://github.com/envoyproxy/gateway
- https://github.com/envoyproxy/gateway/releases/tag/v1.2.7
- https://github.com/envoyproxy/gateway/releases/tag/v1.3.1
- https://pkg.go.dev/vuln/GO-2025-3504
