# [M] OpenBao Inserts Sensitive Information into Log File when processing malformed data

## Summary
Severity: Medium
Advisory: GHSA-8f5r-8cmq-7fmq
CVE: CVE-2025-52893
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-26
Source: https://github.com/advisories/GHSA-8f5r-8cmq-7fmq
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao/sdk/v2` — affected >=0 <2.3.0

## Details
### Impact

OpenBao before v2.3.0 and HashiCorp Vault as of the current v1.19.5 may leak sensitive information in logs when processing malformed data. This is separate from the earlier HCSEC-2025-09 / CVE-2025-4166. 

### Patches

This issue has been fixed in OpenBao v2.3.0 and later.

### Workarounds

Like with HCSEC-2025-09, there is no known workaround except to ensure properly formatted requests from all clients.

### Remediation

Users with the capability to search through server and audit logs for any possible exposed secrets can refer to the following snippets to aid in searching:

Audit Log

```
... "error":"error converting input for field \"password\": expected type 'string', got unconvertible type 'map[string]interface {}', value: '<sensitive data>'" ...
```

Server Log

```
error converting input for field "password": expected type 'string', got unconvertible type 'map[string]interface {}', value: '<sensitive data>'
```

If any matches are found, rotating the affected secret is advised.

### References

See also: https://discuss.hashicorp.com/t/hcsec-2025-09-vault-may-expose-sensitive-information-in-error-logs-when-processing-malformed-data-with-the-kv-v2-plugin/74717

See also: https://github.com/go-viper/mapstructure/releases/tag/v2.3.0

See also: https://github.com/go-viper/mapstructure/pull/105 -> https://github.com/go-viper/mapstructure/commit/ed3f92181528ff776a0324107b8b55026e93766a

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-8f5r-8cmq-7fmq
- https://nvd.nist.gov/vuln/detail/CVE-2025-52893
- https://github.com/go-viper/mapstructure/pull/105
- https://github.com/go-viper/mapstructure/commit/ed3f92181528ff776a0324107b8b55026e93766a
- https://github.com/openbao/openbao/commit/cf5e920badbf96b41253534a3fd5ff5063bf4b30
- https://discuss.hashicorp.com/t/hcsec-2025-09-vault-may-expose-sensitive-information-in-error-logs-when-processing-malformed-data-with-the-kv-v2-plugin/74717
- https://github.com/go-viper/mapstructure/releases/tag/v2.3.0
- github.com/openbao/openbao/sdk/v2/framework
