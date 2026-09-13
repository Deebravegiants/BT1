# [H] Incorrect delegation lookups can make go-tuf download the wrong artifact

## Summary
Severity: High
Advisory: GHSA-4f8r-qqr9-fq8j
CVE: CVE-2024-47534
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-4f8r-qqr9-fq8j
Type: github-advisory

## Affected
- Go: `github.com/theupdateframework/go-tuf/v2` — affected >=0 <2.0.1

## Details
During the ongoing work on the TUF conformance test suite, we have come across a test that reveals what we believe is a bug in go-tuf with security implications. The bug exists in go-tuf delegation tracing and could result in downloading the wrong artifact. 

We have come across this issue in the test in this PR: https://github.com/theupdateframework/tuf-conformance/pull/115.

The test - `test_graph_traversal` - sets up a repository with a series of delegations, invokes the clients `refresh()` and then checks the order in which the client traced the delegations. The test shows that the go-tuf client inconsistently traces the delegations in a wrong way. For example, [during one CI run](https://github.com/theupdateframework/tuf-conformance/pull/115#issuecomment-2275625542), the `two-level-delegations` test case triggered a wrong order. The delegations in this look as such:

```python
"two-level-delegations": DelegationsTestCase(
        delegations=[
            DelegationTester("targets", "A"),
            DelegationTester("targets", "B"),
            DelegationTester("B", "C"),
        ],
        visited_order=["A", "B", "C"],
    ),
```

Here, `targets` delegate to `"A"`, and to `"B"`, and `"B"` delegates to `"C"`. The client should trace the delegations in the order `"A"` then `"B"` then `"C"` but in this particular CI run, go-tuf traced the delegations `"B"->"C"->"A"`.

In a subsequent CI run, this test case did not fail, but [another one did](https://github.com/theupdateframework/tuf-conformance/pull/115#issuecomment-2275640487).

@jku has done a bit of debugging and believes that the returned map of `GetRolesForTarget` returns a map that causes this behavior:

https://github.com/theupdateframework/go-tuf/blob/f95222bdd22d2ac4e5b8ed6fe912b645e213c3b5/metadata/metadata.go#L565-L580

We believe that this map should be an ordered list instead of a map.

## References
- https://github.com/theupdateframework/go-tuf/security/advisories/GHSA-4f8r-qqr9-fq8j
- https://nvd.nist.gov/vuln/detail/CVE-2024-47534
- https://github.com/theupdateframework/tuf-conformance/pull/115
- https://github.com/theupdateframework/go-tuf/commit/edc30b474f5afd4cc603e17149704d5aa605151d
- https://github.com/theupdateframework/go-tuf/commit/f36420caba9edbfdfd64f95a9554c0836d9cf819
- https://github.com/theupdateframework/go-tuf
- https://github.com/theupdateframework/go-tuf/blob/f95222bdd22d2ac4e5b8ed6fe912b645e213c3b5/metadata/metadata.go#L565-L580
- https://pkg.go.dev/vuln/GO-2024-3166
