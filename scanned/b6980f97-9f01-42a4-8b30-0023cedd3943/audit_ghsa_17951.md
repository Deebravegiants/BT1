# [M] GraphQL Armor Max-Depth Plugin Bypass via fragment caching

## Summary
Severity: Medium
Advisory: GHSA-224p-v68g-5g8f
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-08-26
Source: https://github.com/advisories/GHSA-224p-v68g-5g8f
Type: github-advisory

## Affected
- npm: `@escape.tech/graphql-armor-max-depth` — affected >=0 <2.4.2

## Details
### Summary
A query depth restriction using the max-depth can be bypassed if `ignoreIntrospection` is enabled (which is the default configuration) by naming your query/fragment `__schema`.

### Details
In the `countDepth` function, we have the following code that calculates the depth of a used fragment:

```typescript
    } else if (node.kind == Kind.FRAGMENT_SPREAD) {
      if (this.visitedFragments.has(node.name.value)) {
        return this.visitedFragments.get(node.name.value) ?? 0;
      } else {
        this.visitedFragments.set(node.name.value, -1);
      }
      const fragment = this.context.getFragment(node.name.value);
      if (fragment) {
        let fragmentDepth;
        if (this.config.flattenFragments) {
          fragmentDepth = this.countDepth(fragment, parentDepth);
        } else {
          fragmentDepth = this.countDepth(fragment, parentDepth + 1);
        }
        depth = Math.max(depth, fragmentDepth);
        if (this.visitedFragments.get(node.name.value) === -1) {
          this.visitedFragments.set(node.name.value, fragmentDepth);
        }
      }
    }
```

which will calculate the depth of the fragment used in the current node, store the value in `this.visitedFragments` and re-use it in the future to avoid re-calculating the depth for the same fragment.

The issue arises when the same fragment is used multiple times, **at different depths**. The current caching takes into account the depth of the first occurrence, which means if the fragment is re-used later in a higher depth, this cached value is not updated.

So, for example, sending the following query with a max depth of `6`:

```graphql
query {
  books {
    author {
      ...Test
    }
  }
  books {
    author {
      books {
        author {
          ...Test
        }
      }
    }
  }
}
fragment Test on Author {
  books {
    title
  }
}
```

The first use of `Test` fragment does not exceed the defined limit, and this depth will be cached.

In the second use, the fragment is reused in a greater depth, but the `countDepth` function will still use the depth cached, without accounting for the increased depth.

### PoC

Max depth: `6`

```graphql
query {
  books {
    author {
      ...Test
    }
  }
  books {
    author {
      books {
        author {
          ...Test
        }
      }
    }
  }
}
fragment Test on Author {
  books {
    title
  }
}
```

### Impact

This issue affects applications using the GraphQL Armor Depth Limit plugin.

### Fix

This is fixed in [PR#824](https://github.com/Escape-Technologies/graphql-armor/pull/824). We now store only the additional depth contributed by the fragment and add it to the parent depth where the fragment is used (`parentDepth`).

## References
- https://github.com/Escape-Technologies/graphql-armor/security/advisories/GHSA-224p-v68g-5g8f
- https://github.com/Escape-Technologies/graphql-armor/pull/824
- https://github.com/Escape-Technologies/graphql-armor/commit/998986109f8c2313bd61325ddfe7f5dcd48f9232
- https://github.com/Escape-Technologies/graphql-armor
