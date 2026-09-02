### Title
Webhook `shop-domain` / `topic` identity used for tenant dispatch is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before dispatching it to the app's handler, but the HMAC signature it verifies only covers the raw request body. The `shop` (tenant identity) and `topic` values that are handed to the application's webhook handler are read directly from unauthenticated HTTP headers, which are never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over exactly `to_signable_string` (i.e. the body only) and secure-compares it to the `hmac` field, which itself is read from the `hmac-sha256` header: [2](#0-1) [3](#0-2) 

Meanwhile, `shop`, `topic`, and `webhook_id` — the values used to identify *which tenant and event* the payload belongs to — are pulled straight from headers that are completely outside the signed content: [4](#0-3) 

`Registry.process` validates the HMAC and then dispatches to the handler using these unauthenticated header values as the tenant key: [5](#0-4) 

The gem's own documentation states this call "will verify the request did indeed come from Shopify," creating an expectation that `shop` is trustworthy once `process` succeeds: [6](#0-5) 

**The broken identity binding, expressed as an equality that should hold but doesn't:**
`shop used for tenant dispatch (header, unauthenticated)` ≠ `shop bound to the HMAC-verified bytes (body only)`.

Because the HMAC is computed with the app's shared `api_secret_key` over the body alone, any legitimately-signed webhook body a low-privilege attacker can obtain (e.g. from a webhook Shopify sends to their *own* installed/test shop) carries a valid HMAC that is completely independent of the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers. An attacker who can influence the HTTP request that reaches the app's webhook endpoint (e.g. by controlling the raw request assembly, replaying a captured payload, or via a host application that reflects attacker-supplied headers to `Request.new(headers: ...)`) can attach the same valid `(body, hmac)` pair while swapping the `shop-domain` header to a victim shop's domain. `Registry.process` will still pass HMAC validation and will call the application's handler with `shop: request.shop` set to the attacker-chosen value, causing the host application to attribute attacker-influenced webhook data to a shop/tenant that never sent it.

This matches the audit's requested bug class: a field that is *acted on* (`shop`, used as the tenant/session key by downstream `handle` implementations) but *not covered by the HMAC* that is supposed to authenticate the request.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: cross-tenant data attribution. A host application that uses `data.shop` from `WebhookMetadata` (as the gem's own webhook docs recommend: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) to select which shop's session/data store to act on can be made to apply attacker-supplied webhook content to a shop the attacker does not control, since the gem gives no signed guarantee that `shop` corresponds to the entity that produced the HMAC-validated body. This satisfies the "cross-tenant access" criterion for Critical impact, since it is the tenant-identity field itself, not just cosmetic metadata, that is unauthenticated.

### Likelihood Explanation
Exploitability depends on the attacker's ability to get a body+hmac pair signed for *some* shop (trivial if the attacker is a merchant who has installed the app, i.e. an "unprivileged internet user" relative to other shops) and then present it with a different `shop-domain`/`topic` header to the app's webhook endpoint. Whether that header can be attacker-controlled at the transport layer depends on the host application/proxy, so likelihood is moderate rather than certain — but the root cause inside `shopify_api` is unambiguous: the library's own signature check structurally excludes the very fields it hands to the handler as trusted identity.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., require the host app to independently verify `shop` against a known session store before trusting `WebhookMetadata#shop`), and update `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` so that `HmacValidator.validate` fails if any of these header-derived identity fields have been altered relative to what Shopify actually signed.

### Proof of Concept
1. App receives a legitimate Shopify webhook for `shop-a.myshopify.com` with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
2. Attacker (who controls or intercepts the request path to the app's webhook route, e.g. via a component that lets header values be set independently of the signed body) resends `raw_body: B`, `headers: { "shopify-hmac-sha256" => H, "shopify-shop-domain" => "shop-victim.myshopify.com", "shopify-topic" => "orders/create" }`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(api_secret_key, B)` and matches `H` — validation succeeds because only the body is checked (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "shop-victim.myshopify.com", body: JSON.parse(B), ...))` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the host app to process attacker-influenced data as if it belonged to `shop-victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
