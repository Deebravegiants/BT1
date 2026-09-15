# [M] Minder trusts client-provided mapping from repo name to upstream ID

## Summary
Severity: Medium
Advisory: GHSA-q6h8-4j2v-pjg4
CVE: CVE-2024-27093
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-02-26
Source: https://github.com/advisories/GHSA-q6h8-4j2v-pjg4
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0 <0.20240226.1425

## Details
### Summary

When using a modified client or the grpc interface directly, the `RegisterRepository` call accepts _both_ the repository owner / repo **and** the repo_id.  Furthermore, these two are not checked for matching before registering webhooks and data in the database.

### Details

It is possible for an attacker to register a repository with a invalid or differing upstream ID, which causes Minder to report the repository as registered, but not remediate any future changes which conflict with policy (because the webhooks for the repo do not match any known repository in the database).  When attempting to register a repo with a different repo ID, the registered provider must have admin on the named repo, or a 404 error will result.  Similarly, if the stored provider token does not have repo access, then the remediations will not apply successfully.  Lastly, it appears that reconciliation actions do not execute against repos with this type of mismatch.

### PoC

With an RPC like the following text proto:

```
context {
  ...
}
repository {
  owner: "Stacklok-Demo-Org"
  repo: "python-app"
  # repo_id is defaulted to 0
}
```

I was able to produce the following `minder` output:

```
+--------------------------------------+--------------------------------------+----------+-------------+-------------------+------------+
|                  ID                  |               PROJECT                | PROVIDER | UPSTREAM ID |       OWNER       |    NAME    |
+--------------------------------------+--------------------------------------+----------+-------------+-------------------+------------+
| da3acba4-ef66-4d9b-b41e-250869107fd5 | f9f4aef0-74af-4909-a0c3-0e8ac7fbc38d | github   |           0 | Stacklok-Demo-Org | python-app |
+--------------------------------------+--------------------------------------+----------+-------------+-------------------+------------+
| 7cf8f7b8-b19b-40dd-a96b-b88bb1ef5563 | f9f4aef0-74af-4909-a0c3-0e8ac7fbc38d | github   |   762029128 | evankanderson     | bad-python |
+--------------------------------------+--------------------------------------+----------+-------------+-------------------+------------+
```

```
$ gh api repos/Stacklok-Demo-Org/python-app | jq .id                  
762029128
```

I've registered bad-python with the ID of python-app, and python-app with an ID of 0.

### Impact

This appears to primarily be a potential denial-of-service vulnerability.

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-q6h8-4j2v-pjg4
- https://nvd.nist.gov/vuln/detail/CVE-2024-27093
- https://github.com/stacklok/minder/commit/53868a878e93f29c43437f96dbc990b548e48d1d
- https://github.com/stacklok/minder
- https://pkg.go.dev/vuln/GO-2024-2582
