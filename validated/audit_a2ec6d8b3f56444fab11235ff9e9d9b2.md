### Title
Webhook shop identity is trusted from an unauthenticated header while the HMAC only signs the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload solely from the raw request body, while the `shop` (and `topic`/`webhook_id`) attribution comes from HTTP headers that are never included in the signed content. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body/HMAC pair validates and then dispatches the handler using the header-derived, unauthenticated `shop` value — breaking the binding `shop_verified_by_hmac == shop_used_by_handler`.

### Finding Description
The signable content for a webhook request is defined as just the raw body: [1](#0-0) 

and the shop, topic, and webhook id are pulled straight from HTTP headers, none of which participate in the HMAC computation: [2](#0-1) 

`HmacValidator.validate` only proves that the raw body was signed with the app's shared `client_secret` — it says nothing about which shop the body belongs to, since `to_signable_string` never includes the shop: [3](#0-2) 

`Registry.process` then trusts `request.shop` (header-derived) once the body HMAC passes, and dispatches it straight to the app's handler as the authoritative tenant identity: [4](#0-3) 

Because the app's `client_secret` (and therefore the HMAC key) is shared across every shop that installs the app, any merchant who legitimately installs the app on their own store can capture a genuine `(raw_body, hmac)` pair from a webhook Shopify sends them (e.g. by placing a test order to trigger `orders/create`). That attacker — unprivileged with respect to any other merchant's store — can then replay the exact same body and HMAC to the app's public webhook endpoint while forging the `X-Shopify-Shop-Domain` header to name a victim shop. `HmacValidator.validate` still succeeds because the body is untouched, and `Registry.process` calls the handler with `shop: <victim-shop-domain>`, breaking the intended equality between "shop whose secret produced this HMAC" and "shop the handler believes it received data for."

### Impact Explanation
This crosses a tenant boundary: the SDK hands the consuming application data that is falsely attributed to a shop the attacker does not control, while claiming HMAC-verified authenticity. Any host application logic that trusts `WebhookMetadata#shop` for tenant-scoped actions (looking up/refreshing tokens, updating billing state, triggering business logic keyed by shop) can be manipulated into acting on/for the wrong tenant using attacker-supplied payload content. This matches the "Critical - cross-tenant access" impact category, since the identity binding the whole webhook trust model depends on (`shop` field) is not actually covered by the cryptographic check the gem performs.

### Likelihood Explanation
Requires only: (1) being any merchant capable of installing the target app once (an ordinary business signup, not a privileged account) to receive a legitimate signed webhook, and (2) sending an HTTP POST with attacker-chosen headers to the app's public webhook endpoint. No access to `api_secret_key` or any victim credential is needed, since the replayed body+HMAC pair is valid on its own merit — only the header is forged. This is directly exploitable through the gem's own `Webhooks::Request` / `Webhooks::Registry.process` API without relying on any misuse by the host app beyond using the documented `shop` field for identity.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is cryptographically checked, or otherwise require the caller to supply/verify the expected shop out-of-band (e.g., verifying the target shop has an active, matching installation/session before dispatch), so that `Registry.process` cannot attribute a validly-signed body to an arbitrary shop supplied only via an unauthenticated header.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) to capture a real `(raw_body, X-Shopify-Hmac-Sha256)` pair issued by Shopify using the app's shared `client_secret`.
2. Attacker POSTs this exact `raw_body` with the exact same `X-Shopify-Hmac-Sha256` header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only checks `raw_body`, which is untouched.
4. `ShopifyAPI::Webhooks::Registry.process` calls the registered handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)`, and the host app now processes attacker-controlled webhook content believing it is authentic data belonging to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
