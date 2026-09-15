# [M] Missing Role Based Access Control for the REST handlers in bleve/http package

## Summary
Severity: Medium
Advisory: GHSA-9w9f-6mg8-jp7w
CVE: CVE-2022-31022
CWE: CWE-288, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-9w9f-6mg8-jp7w
Type: github-advisory

## Affected
- Go: `github.com/blevesearch/bleve` — affected >=0
- Go: `github.com/blevesearch/bleve/v2` — affected >=0 <2.5.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Bleve includes HTTP utilities under bleve/http package, that are used by its sample application. 
(https://github.com/blevesearch/bleve-explorer)
These HTTP methods paves way for exploitation of a node’s filesystem where the bleve index resides, 
if the user has used bleve’s own HTTP (bleve/http) handlers for exposing the access to the indexes. 
For instance, the CreateIndexHandler (http/index_create.go) and DeleteIndexHandler (http/index_delete.go) 
enable an attacker to create a bleve index (directory structure) anywhere where the user running the server 
has the write permissions and to delete recursively any directory owned by the same user account.
 
Users who have used the bleve/http package for exposing access to bleve index without the explicit 
handling for the Role Based Access Controls(RBAC) of the index assets would be impacted.


### Patches
_Has the problem been patched? What versions should users upgrade to?_

**No**. The http package is purely intended to be used for demonstration purposes. 
And bleve is never designed to be handling the RBACs or it was ever advertised to be used in that way. 
Hence the collaborators of this project have decided to stay away from adding any authentication or 
authorization to bleve project at the moment.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

The bleve/http package is mainly for demonstration purposes and it lacks exhaustive validation of the user 
inputs as well as any authentication and authorization measures. 
So it is recommended to not use that in production use cases.

### For more information
If you have any questions or comments about this advisory:
* Open an issue [here](https://github.com/blevesearch/bleve/issues).
* Email us at [mailto:security@couchbase.com, fts-team@couchbase.com].

## References
- https://github.com/blevesearch/bleve/security/advisories/GHSA-9w9f-6mg8-jp7w
- https://nvd.nist.gov/vuln/detail/CVE-2022-31022
- https://github.com/blevesearch/bleve/commit/1c7509d6a17d36f265c90b4e8f4e3a3182fe79ff
- https://github.com/blevesearch/bleve/commit/af9e3111dadfedf9d30f0448506b4a57fecc8550
- https://pkg.go.dev/vuln/GO-2022-0470
- github.com/blevesearch/bleve
