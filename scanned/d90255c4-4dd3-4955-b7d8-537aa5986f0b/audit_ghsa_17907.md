# [M] GraphQL Armor Max-Depth Plugin Bypass via Introspection Query Obfuscation

## Summary
Severity: Medium
Advisory: GHSA-hmfr-rx46-4jx2
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-hmfr-rx46-4jx2
Type: github-advisory

## Affected
- npm: `@escape.tech/graphql-armor-max-depth` — affected >=0 <2.4.2

## Details
### Summary
A query depth restriction using the `max-depth` property can be bypassed if `ignoreIntrospection` is enabled (which is the default configuration) by naming your query/fragment `__schema`.

### Details
At the start of the `countDepth` function, we have the following check for the `ignoreIntrospection` option:

```typescript
    if (this.config.ignoreIntrospection && 'name' in node && node.name?.value === '__schema') {
        return 0;
    }
```

However, the `node` can be one of: `FieldNode`, `FragmentDefinitionNode`, `InlineFragmentNode`, `OperationDefinitionNode`, `FragmentSpreadNode`.

For example, consider sending the following query:

```graphql
query hello {
  books {
    title
  }
}
```

This would create an `OperationDefinitionNode` where `node.name.value == 'hello'`

The proper way to handle this is to check explicitly for the `__schema` field, which corresponds to a `FieldNode`.

The fix is

```typescript
    if (
      this.config.ignoreIntrospection &&
      'name' in node &&
      node.name?.value === '__schema' &&
      node.kind === Kind.FIELD
    ) {
      return 0;
    }
```

This ensures that the node is explicitly a `FieldNode`.

### PoC

Max depth: `6`

```graphql
query {
  books {
    author {
      books {
        author {
          ...__schema
        }
      }
    }
  }
}
fragment __schema on Author {
  books {
    title
  }
}
```

### Impact

This issue affects applications using the GraphQL Armor Depth Limit plugin with `ignoreIntrospection` enabled.

### Fix

This is fixed in [PR#823](https://github.com/Escape-Technologies/graphql-armor/pull/823)

## References
- https://github.com/Escape-Technologies/graphql-armor/security/advisories/GHSA-hmfr-rx46-4jx2
- https://github.com/Escape-Technologies/graphql-armor/pull/823
- https://github.com/Escape-Technologies/graphql-armor/commit/1f923bc09f5f053f60b6ba2bd419d4b94cbe1db3
- https://github.com/Escape-Technologies/graphql-armor
