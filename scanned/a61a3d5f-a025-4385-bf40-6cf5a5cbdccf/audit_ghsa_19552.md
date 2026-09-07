# [M] GraphQL Armor Cost-Limit Plugin Bypass via Introspection Query Obfuscation

## Summary
Severity: Medium
Advisory: GHSA-733v-p3h5-qpq7
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-733v-p3h5-qpq7
Type: github-advisory

## Affected
- npm: `@escape.tech/graphql-armor-cost-limit` — affected >=0 <2.4.2

## Details
### Summary
A query cost restriction using the `cost-limit` can be bypassed if `ignoreIntrospection` is enabled (which is the default configuration) by naming your query/fragment `__schema`.

### Details
At the start of the `computeComplexity` function, we have the following check for `ignoreIntrospection` option:

```ts
    if (this.config.ignoreIntrospection && 'name' in node && node.name?.value === '__schema') {
      return 0;
    }
```

However, the `node` can be `FieldNode | FragmentDefinitionNode | InlineFragmentNode | OperationDefinitionNode | FragmentSpreadNode`

So, for example, sending the following query

```gql
query hello {
  books {
    title
  }
}
```

would create an `OperationDefinitionNode` with `node.name.value == 'hello'`

The proper way to handle this would be to check for the `__schema` field, which would create a `FieldNode`.

The fix is

```ts
    if (
      this.config.ignoreIntrospection &&
      'name' in node &&
      node.name?.value === '__schema' &&
      node.kind === Kind.FIELD
    ) {
      return 0;
    }
```

to assert that the node must be a `FieldNode`

### PoC
```gql
query  {
  ...__schema
}

fragment __schema on Query {
  books {
    title
    author
  }
}
```

```gql
query __schema {
  books {
    title
    author
  }
}
```

### Impact
Applications using GraphQL Armor Cost Limit plugin with `ignoreIntrospection` enabled.

### Fix:
Fixed on [772](https://github.com/Escape-Technologies/graphql-armor/pull/772). A quick patch would be to set `ignoreIntrospection` to false.

## References
- https://github.com/Escape-Technologies/graphql-armor/security/advisories/GHSA-733v-p3h5-qpq7
- https://github.com/Escape-Technologies/graphql-armor/pull/772
- https://github.com/Escape-Technologies/graphql-armor/commit/5a329541cf32a359ee1f69748738f91231b26eba
- https://github.com/Escape-Technologies/graphql-armor
