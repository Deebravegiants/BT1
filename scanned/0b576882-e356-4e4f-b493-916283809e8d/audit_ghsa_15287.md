# [H] Apollo Query Planner and Apollo Gateway may infinitely loop on sufficiently complex queries

## Summary
Severity: High
Advisory: GHSA-fmj9-77q8-g6c4
CVE: CVE-2024-43414
CWE: CWE-673, CWE-674
Ecosystem: crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-fmj9-77q8-g6c4
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=0 <1.52.1
- npm: `@apollo/query-planner` — affected >=2.0.0 <2.8.5
- npm: `@apollo/gateway` — affected >=2.0.0 <2.8.5

## Details
### Impact
Instances of @apollo/query-planner >=2.0.0 and <2.8.5 are impacted by a denial-of-service vulnerability. @apollo/gateway versions >=2.0.0 and < 2.8.5 and Apollo Router <1.52.1 are also impacted through their use of @apollo/query-planner. 

If @apollo/query-planner is asked to plan a sufficiently complex query, it may loop infinitely and never complete. This results in unbounded memory consumption and either a crash or out-of-memory (OOM) termination.

This issue can be triggered if you have at least one non-`@key` field that can be resolved by multiple subgraphs. To identify these shared fields, the schema for each subgraph must be reviewed. The mechanism to identify shared fields varies based on the version of Federation your subgraphs are using.

You can check if your subgraphs are using Federation 1 or Federation 2 by reviewing their schemas. Federation 2 subgraph schemas will contain a `@link` directive referencing the version of Federation being used while Federation 1 subgraphs will not. For example, in a Federation 2 subgraph, you will find a line like `@link(url: "https://specs.apollo.dev/federation/v2.0")`. If a similar `@link` directive is not present in your subgraph schema, it is using Federation 1. Note that a supergraph can contain a mix of Federation 1 and Federation 2 subgraphs.

**To review Federation 1 subgraphs for impact:**

In Federation 1 subgraphs, fields are implicitly shareable across subgraphs. To review for impact, you will need to review for cases where multiple subgraphs can resolve the same field. For example: 

```graphql
# Subgraph 1
type Query {
  field: Int
}

# Subgraph 2
type Query {
  field: Int
}
```


**To review Federation 2 subgraphs for impact:**

In Federation 2 subgraphs, fields must be explicitly defined as shareable across subgraphs. This is done via the `@shareable` directive. For example:

```graphql
# Subgraph 1
@link(url: "https://specs.apollo.dev/federation/v2.0")
type Query {
  field: Int @shareable
}

# Subgraph 2
@link(url: "https://specs.apollo.dev/federation/v2.0")
type Query {
  field: Int @shareable
}
```

### Impact Detail

This issue results from the Apollo query planner attempting to use a `Number` exceeding Javascript’s `Number.MAX_VALUE` in some cases. In Javascript, `Number.MAX_VALUE` is (2^1024 - 2^971).

When the query planner receives an inbound graphql request, it breaks the query into pieces and for each piece, generates a list of potential execution steps to solve the piece. These candidates represent the steps that the query planner will take to satisfy the pieces of the larger query. As part of normal operations, the query planner requires and calculates the number of possible query plans for the total query. That is, it needs the product of the number of query plan candidates for each piece of the query. Under normal circumstances, after generating all query plan candidates and calculating the number of all permutations, the query planner moves on to stack rank candidates and prune less-than-optimal options. 

In particularly complex queries, especially those where fields can be solved through multiple subgraphs, this can cause the number of all query plan permutations to balloon. In worst-case scenarios, this can end up being a number larger than `Number.MAX_VALUE`. In Javascript, if `Number.MAX_VALUE` is exceeded, Javascript represents the value as “infinity”. If the count of candidates is evaluated as infinity, the component of the query planner responsible for pruning less-than-optimal query plans does not actually prune candidates, causing the query planner to evaluate many orders of magnitude more query plan candidates than necessary.

A given graph’s exposure to this issue varies based on its complexity. Consider the following Federation 2 subgraphs: 

```graphql
# Subgraph 1
type Query {
  field: Int @shareable
}

# Subgraph 2
type Query {
  field: Int @shareable
}
```

The query planner can solve requests for `Query.field` in one of two ways - either by querying subgraph 1 or subgraph 2. 

The following query with 1024 aliased fields would trigger this issue because 2^1024 > `Number.MAX_VALUE`:  

```graphql
query {
  field_1: field
  field_2: field
  # ...
  field_1023: field
  field_1024: field
}
```


However, in a graph that provided 5 options to solve a given field, the bug could be encountered in a query that aliased the field approximately 440 times.


### Patches
@apollo/query-planner 2.8.5
@apollo/gateway 2.8.5
Apollo Router 1.52.1

### Workarounds
This issue can be avoided by ensuring there are no fields resolvable from multiple subgraphs. If all subgraphs are using Federation 2, you can confirm that you are not impacted by ensuring that none of your subgraph schemas use the `@shareable` directive. If you are using Federation 1 subgraphs, you will need to validate that there are no fields resolvable by multiple subgraphs. 

Note that a supergraph can contain a mix of Federation 1 and Federation 2 subgraphs. 

If you do have fields resolvable by multiple subgraphs, changing this behavior in response to this issue may be risky to the operation of your supergraph. We recommend that you update to a patched version of either Apollo Router or Apollo Gateway.

Apollo customers with an enterprise entitlement using the Apollo Router can also mitigate much of the risk from this issue by implementing [Apollo’s Persisted Queries (PQ) feature](https://www.apollographql.com/docs/router/configuration/persisted-queries). With PQ enabled, the Apollo Router will only execute safelisted queries. While customers would need to ensure that queries that induce this issue are not added to the safelist, PQs would mitigate the risk of clients submitting ad hoc queries that exploit this issue.

### References

[Additional information on Query Plans](https://www.apollographql.com/docs/federation/query-plans/)

## References
- https://github.com/apollographql/federation/security/advisories/GHSA-fmj9-77q8-g6c4
- https://nvd.nist.gov/vuln/detail/CVE-2024-43414
- https://github.com/apollographql/router/commit/e309c9bb5a48c1304ff69c88b7eabdd08c26bf45
- https://github.com/apollographql/federation
- https://www.apollographql.com/docs/federation/query-plans
- https://www.apollographql.com/docs/router/configuration/persisted-queries
