# [H] Denial of Service in http-swagger

## Summary
Severity: High
Advisory: GHSA-xg75-q3q5-cqmv
CVE: CVE-2022-24863
CWE: CWE-400, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-xg75-q3q5-cqmv
Type: github-advisory

## Affected
- Go: `github.com/swaggo/http-swagger` — affected >=0 <1.2.6

## Details
### Impact
Allows an attacker to perform a DOS attack consisting of memory exhaustion on the host system.

### Patches
Yes. Please upgrade to v1.2.6.

### Workarounds
A workaround is to restrict the path prefix to the "GET" method. As shown below
```
func main() {
	r := mux.NewRouter()

	r.PathPrefix("/swagger/").Handler(httpSwagger.Handler(
		httpSwagger.URL("http://localhost:1323/swagger/doc.json"), //The url pointing to API definition
		httpSwagger.DeepLinking(true),
		httpSwagger.DocExpansion("none"),
		httpSwagger.DomID("#swagger-ui"),
	)).Methods(http.MethodGet)
```

### References
Reporter dongguangli from https://www.huoxian.cn/ company

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [http-swagger](https://github.com/swaggo/http-swagger/issues)

## References
- https://github.com/swaggo/http-swagger/security/advisories/GHSA-xg75-q3q5-cqmv
- https://nvd.nist.gov/vuln/detail/CVE-2022-24863
- https://github.com/swaggo/http-swagger/pull/62
- https://github.com/swaggo/http-swagger/commit/b7d83e8fba85a7a51aa7e45e8244b4173f15049e
- https://cosmosofcyberspace.github.io/improper_http_method_leads_to_xss/poc.html
- https://github.com/swaggo/http-swagger
- https://github.com/swaggo/http-swagger/releases/tag/v1.2.6
