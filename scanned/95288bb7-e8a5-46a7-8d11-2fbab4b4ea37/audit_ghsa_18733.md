# [H] OpenBao has potential Denial of Service vulnerability when processing malicious unauthenticated JSON requests

## Summary
Severity: High
Advisory: GHSA-g46h-2rq9-gw5m
CVE: CVE-2025-59043
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-g46h-2rq9-gw5m
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <2.4.1

## Details
### Summary

JSON objects after decoding might use more memory than their serialized version. It is possible to tune a JSON to maximize the factor between serialized memory usage and deserialized memory usage (similar to a zip bomb). While reproducing the issue, we could reach a factor of about 35. This can be used to circumvent the [`max_request_size` (https://openbao.org/docs/configuration/listener/tcp/) configuration parameter, which is meant to protect against Denial of Service attacks, and also makes Denial of Service attacks easier in general, as the attacker needs much less resources.

### Details

The request body is parsed into a `map[string]interface{}` https://github.com/openbao/openbao/blob/788536bd3e10818a7b4fb00aac6affc23388e5a9/http/logical.go#L50 very early in the request handling chain (before authentication), which means an attacker can send a specifically crafted JSON object and cause an OOM crash. Additionally, for simpler requests with large numbers of strings, the audit subsystem can consume large quantities of CPU. 

To remediate, set `max_request_json_memory` and `max_request_json_strings`.

### Impact

- Unauthenticated Denial of Service

### Resources

This issue was disclosed directly to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-24-vault-denial-of-service-though-complex-json-payloads/76393
- https://nvd.nist.gov/vuln/detail/CVE-2025-6203

HashiCorp attributes the problem to the audit subsystem. For OpenBao, it was noted the problem was additionally in the requests handling logic.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-g46h-2rq9-gw5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-59043
- https://nvd.nist.gov/vuln/detail/CVE-2025-6203
- https://github.com/openbao/openbao/pull/1756
- https://github.com/openbao/openbao/commit/d418f238bc99adc72c73109faf574cc2b672880c
- https://discuss.hashicorp.com/t/hcsec-2025-24-vault-denial-of-service-though-complex-json-payloads/76393
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/blob/788536bd3e10818a7b4fb00aac6affc23388e5a9/http/logical.go#L50
