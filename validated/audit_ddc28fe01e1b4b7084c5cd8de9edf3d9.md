### No vulnerability found for this question.

The `AuthScopes#==`/`#hash` behavior in [1](#0-0)  is not used as an authorization gate anywhere in the gem. Scope enforcement (the actual security-relevant check) is performed exclusively via `covers?`, which compares `expanded_scopes` against `compressed_scopes` [2](#0-1) , and the `implied_scope` expansion is prefix-aware: an `unauthenticated_write_x` only ever implies `unauthenticated_read_x`, never plain `read_x` [3](#0-2) . This is confirmed by the existing test `test_unauthenticated_is_not_implied_by_authenticated_access`, which asserts that `unauthenticated_read_orders` is **not** equal to `read_orders` or `write_orders` [4](#0-3) , and by `test_write_is_the_same_access_as_read_write_on_the_same_unauthenticated_resource`, which shows the write→read equivalence is scoped strictly within the same `unauthenticated_` namespace, matching Shopify's actual OAuth scope semantics [5](#0-4) .

`==`/`hash` are used only for value-equality comparisons (e.g., in `Session#==`/tests comparing expected vs. actual sessions), not as a permission check; `Session#scope` is itself populated only from the OAuth token exchange response returned by Shopify (`Session.from`), not from unauthenticated attacker-supplied request data [6](#0-5) . There is no code path where an attacker-controlled scope string reaches `==`/`hash` as a substitute for the `covers?` authorization check, so the claimed divergence between "effective permissions" and equality comparison does not translate into an exploitable scope or expiry bypass.

### Citations

**File:** lib/shopify_api/auth/auth_scopes.rb (L23-26)
```ruby
      sig { params(auth_scopes: AuthScopes).returns(T::Boolean) }
      def covers?(auth_scopes)
        auth_scopes.compressed_scopes <= expanded_scopes
      end
```

**File:** lib/shopify_api/auth/auth_scopes.rb (L38-50)
```ruby
      sig { params(other: T.nilable(AuthScopes)).returns(T::Boolean) }
      def ==(other)
        !other.nil? &&
          other.class == self.class &&
          compressed_scopes == other.compressed_scopes
      end

      alias_method :eql?, :==

      sig { returns(Integer) }
      def hash
        compressed_scopes.hash
      end
```

**File:** lib/shopify_api/auth/auth_scopes.rb (L68-72)
```ruby
      sig { params(scope: String).returns(T.nilable(String)) }
      def implied_scope(scope)
        is_write_scope = scope =~ /\A(unauthenticated_)?write_(.*)\z/
        "#{Regexp.last_match(1)}read_#{Regexp.last_match(2)}" if is_write_scope
      end
```

**File:** test/auth/auth_scopes_test.rb (L26-33)
```ruby
      def test_write_is_the_same_access_as_read_write_on_the_same_unauthenticated_resource
        unauthenticated_read_write_orders = ShopifyAPI::Auth::AuthScopes.new(
          ["unauthenticated_read_orders", "unauthenticated_write_orders"],
        )
        unauthenticated_write_orders = ShopifyAPI::Auth::AuthScopes.new(["unauthenticated_write_orders"])

        assert_equal(unauthenticated_write_orders, unauthenticated_read_write_orders)
      end
```

**File:** test/auth/auth_scopes_test.rb (L49-56)
```ruby
      def test_unauthenticated_is_not_implied_by_authenticated_access
        unauthenticated_orders = ShopifyAPI::Auth::AuthScopes.new(["unauthenticated_read_orders"])
        authenticated_read_orders = ShopifyAPI::Auth::AuthScopes.new(["read_orders"])
        authenticated_write_orders = ShopifyAPI::Auth::AuthScopes.new(["write_orders"])

        refute_equal(unauthenticated_orders, authenticated_read_orders)
        refute_equal(unauthenticated_orders, authenticated_write_orders)
      end
```

**File:** lib/shopify_api/auth/session.rb (L76-76)
```ruby
        @scope = T.let(AuthScopes.new(scope), AuthScopes)
```
