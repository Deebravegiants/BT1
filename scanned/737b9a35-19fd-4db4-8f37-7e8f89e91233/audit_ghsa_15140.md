# [H] Authenticated (user role) SQL injection in `OrderAndPaginate` (GHSL-2023-270)

## Summary
Severity: High
Advisory: GHSA-h374-mm57-879c
CVE: CVE-2024-22196
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-01-11
Source: https://github.com/advisories/GHSA-h374-mm57-879c
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0 <1.9.10-0.20231219195202-ec93ab05a3ec

## Details
### Summary
The [`OrderAndPaginate`](https://github.com/0xjacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/model/model.go#L99C4) function is used to order and paginate data. It is defined as follows:
```go
func OrderAndPaginate(c *gin.Context) func(db *gorm.DB) *gorm.DB {
	return func(db *gorm.DB) *gorm.DB {
		sort := c.DefaultQuery("order", "desc")

		order := fmt.Sprintf("`%s` %s", DefaultQuery(c, "sort_by", "id"), sort)
		db = db.Order(order)

		...
	}
}
```
By using [`DefaultQuery`](https://github.com/0xjacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/model/model.go#L278-L287), the `"desc"` and `"id"` values are used as default values if the query parameters are not set. Thus, the `order` and `sort_by` query parameter are user-controlled and are being appended to the `order` variable without any sanitization.
The same happens with [`SortOrder`](https://github.com/0xjacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/model/model.go#L91), but it doesn't seem to be used anywhere.
```go
func SortOrder(c *gin.Context) func(db *gorm.DB) *gorm.DB {
	return func(db *gorm.DB) *gorm.DB {
		sort := c.DefaultQuery("order", "desc")
		order := fmt.Sprintf("`%s` %s", DefaultQuery(c, "sort_by", "id"), sort)
		return db.Order(order)
	}
}
```
This issue was found using CodeQL for Go: [Database query built from user-controlled sources](https://codeql.github.com/codeql-query-help/go/go-sql-injection/).

#### Proof of Concept
> Based on [this setup](https://github.com/0xJacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/README.md?plain=1#L210) using `uozi/nginx-ui:v2.0.0-beta.7`.
In order to exploit this issue, we need to find a place where the `OrderAndPaginate` function is used. We can find it in the `GET /api/dns_credentials` endpoint.
```go
func GetDnsCredentialList(c *gin.Context) {
	cosy.Core[model.DnsCredential](c).SetFussy("provider").PagingList()
}
```
The `PagingList` function is defined as follows:
```go
func (c *Ctx[T]) PagingList() {
	data, ok := c.PagingListData()
	if ok {
		c.ctx.JSON(http.StatusOK, data)
	}
}
```
And the `PagingListData` function is defined as follows:
```go
func (c *Ctx[T]) PagingListData() (*model.DataList, bool) {
	result, ok := c.result()
	if !ok {
		return nil, false
	}

	result = result.Scopes(c.OrderAndPaginate())
	...
}
```
Using the following request, an attacker can retrieve arbitrary values by checking the order used by the query. That is, the result of the comparison will make the response to be ordered in a specific way.
```http
GET /api/dns_credentials?sort_by=(CASE+WHEN+(SELECT+1)=1+THEN+id+ELSE+updated_at+END)+ASC+--+ HTTP/1.1
Host: 127.0.0.1:8080
Authorization: <<JWT TOKEN>
```
You can notice the order change by changing `=1` to `=2`, and so the comparison will return `false` and the order will be `updated_at` instead of `id`.

### Impact
This issue may lead to `Information Disclosure`

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-h374-mm57-879c
- https://nvd.nist.gov/vuln/detail/CVE-2024-22196
- https://github.com/0xJacky/nginx-ui/commit/ec93ab05a3ecbb6bcf464d9dca48d74452df8a5b
- https://github.com/0xJacky/nginx-ui
- https://github.com/0xjacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/model/model.go#L278-L287
- https://github.com/0xjacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/model/model.go#L91
- https://github.com/0xjacky/nginx-ui/blob/04bf8ec487f06ab17a9fb7f34a28766e5f53885e/model/model.go#L99C4
