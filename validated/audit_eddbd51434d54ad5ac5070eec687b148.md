### Title
Webhook shop-domain identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable payload using only the raw request body, while the `shop` identity used to route and label webhook data comes from an unsigned HTTP header. Because a single `api_secret_key` is shared across every shop that installs the app, any merchant who legitimately receives a validly-signed webhook for their own store can replay that same body/HMAC pair while forging the `shop-domain` header to impersonate a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, by contrast, is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately forwards `request.shop` to the handler as the tenant identity, with no additional binding check between the verified bytes and the shop claim: [3](#0-2) 

`HmacValidator.validate_signature` computes the HMAC using the single, app-wide `Context.api_secret_key` (or `old_api_secret_key`) — the same secret is valid for every shop that has installed the app, not per-tenant: [4](#0-3) 

The broken identity binding is:
`verified(secret, body) == true` should imply `shop == the shop that produced this body`, but instead the gem only checks `verified(secret, body) == true` and trusts an independent, unauthenticated header for `shop`. Since `secret` is shared across all tenants of the app, any merchant that receives one authentic webhook for their own shop possesses a `(body, hmac)` pair that will pass validation for the app in general — not just for their own shop. Re-sending that same body/HMAC with a different `shopify-shop-domain` header value causes the app to process attacker-supplied content while `WebhookMetadata.shop` is falsely labeled as the victim shop: [5](#0-4) 

Downstream host applications rely on `WebhookMetadata#shop` (and the equivalent value from `test/webhooks/registry_test.rb`'s handler assertions confirm this is the field apps key persistence/business logic on) to decide which tenant's data to create/update/delete, so this is a genuine cross-tenant confusion, not merely a documentation gap.

### Impact Explanation
This crosses a tenant boundary without requiring the app's `api_secret_key`, an access token, or any privileged credential — only requiring that the attacker be one of the app's own (unprivileged relative to other merchants) installed shops, from which they can capture one legitimate webhook delivery. Replaying it with a forged shop header lets that shop's data or actions be attributed to, or injected into, a different merchant's tenant context inside the host application, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Webhook payloads (and their HMAC) are visible to the shop owner receiving them (e.g., via their own webhook endpoint logs, a debugging proxy, or a `orders/create` test payload with attacker-controlled cart/order content). No secret material or elevated privilege is needed — only capturing one's own valid `(body, hmac)` pair and re-POSTing it with a different `shop-domain` header value to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`) into the signed material, or otherwise cryptographically tie the shop claim to the verified bytes — e.g., require host applications to independently confirm that `request.shop` corresponds to a shop with an active, matching installation/session before trusting it, or move to per-shop webhook secrets so a valid HMAC for one shop cannot validate spoofed content claiming to originate from another shop.

### Proof of Concept
1. App merchant A (attacker, has legitimately installed the app) receives a real webhook POST at their configured endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker resends the same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only recomputes the HMAC over `B` using the shared `api_secret_key` — it never inspects `shop-domain`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the registered handler with `shop: "victim-shop.myshopify.com"` and `body` = the attacker's chosen payload `B`, causing the host application to act on attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
