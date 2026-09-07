# [M] mapstructure May Leak Sensitive Information in Logs When Processing Malformed Data

## Summary
Severity: Medium
Advisory: GHSA-fv92-fjc5-jj9h
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-fv92-fjc5-jj9h
Type: github-advisory

## Affected
- Go: `github.com/go-viper/mapstructure/v2` — affected >=0 <2.3.0

## Details
### Summary

Use of this library in a security-critical context may result in leaking sensitive information, if used to process sensitive fields.

### Details

OpenBao (and presumably HashiCorp Vault) have surfaced error messages from `mapstructure` as follows:

https://github.com/openbao/openbao/blob/98c3a59c040efca724353ca46ca79bd5cdbab920/sdk/framework/field_data.go#L43-L50

```go
			_, _, err := d.getPrimitive(field, schema)
			if err != nil {
				return fmt.Errorf("error converting input for field %q: %w", field, err)
			}
```

where this calls `mapstructure.WeakDecode(...)`: https://github.com/openbao/openbao/blob/98c3a59c040efca724353ca46ca79bd5cdbab920/sdk/framework/field_data.go#L181-L193

```go

func (d *FieldData) getPrimitive(k string, schema *FieldSchema) (interface{}, bool, error) {
	raw, ok := d.Raw[k]
	if !ok {
		return nil, false, nil
	}

	switch t := schema.Type; t {
	case TypeBool:
		var result bool
		if err := mapstructure.WeakDecode(raw, &result); err != nil {
			return nil, false, err
		}
		return result, true, nil
```

Notably, `WeakDecode(...)` eventually calls one of the decode helpers, which surfaces the original value:

https://github.com/go-viper/mapstructure/blob/1a66224d5e54d8757f63bd66339cf764c3292c21/mapstructure.go#L679-L686

https://github.com/go-viper/mapstructure/blob/1a66224d5e54d8757f63bd66339cf764c3292c21/mapstructure.go#L726-L730

https://github.com/go-viper/mapstructure/blob/1a66224d5e54d8757f63bd66339cf764c3292c21/mapstructure.go#L783-L787

& more.

### PoC

To reproduce with OpenBao:

```
$ podman run -p 8300:8300 openbao/openbao:latest server -dev -dev-root-token-id=root -dev-listen-address=0.0.0.0:8300
```

and in a new tab:

```
$ BAO_TOKEN=root BAO_ADDR=http://localhost:8300 bao auth enable userpass
Success! Enabled userpass auth method at: userpass/
$ curl -X PUT -H "X-Vault-Request: true" -H "X-Vault-Token: root" -d '{"password":{"asdf":"my-sensitive-value"}}' "http://localhost:8300/v1/auth/userpass/users/adsf"
{"errors":["error converting input for field \"password\": '' expected type 'string', got unconvertible type 'map[string]interface {}', value: 'map[asdf:my-sensitive-value]'"]}
```

### Impact

This is an information disclosure bug with little mitigation. See https://discuss.hashicorp.com/t/hcsec-2025-09-vault-may-expose-sensitive-information-in-error-logs-when-processing-malformed-data-with-the-kv-v2-plugin/74717 for a previous version. That version was fixed, but this is in the second part of that error message (starting at `'' expected a map, got 'string'` -- when the field type is `string` and a `map` is provided, we see the above information leak -- the previous example had a `map` type field with a `string` value provided).

This was rated 4.5 Medium by HashiCorp in the past iteration.

## References
- https://github.com/go-viper/mapstructure/security/advisories/GHSA-fv92-fjc5-jj9h
- https://github.com/go-viper/mapstructure
