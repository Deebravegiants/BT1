### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant replay/relabeling of a validly-signed webhook - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` and `topic` values that the registry dispatches on are taken from unauthenticated HTTP headers. This is the same class of bug as the BPLP report: a value that is *acted on* (here, the tenant identity and the dispatch key) is not bound by the cryptographic check that is supposed to authenticate the whole message.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` and `shopify-topic` / `x-shopify-topic` headers, which are never mixed into the signed material: [2](#0-1) 

`Registry.process` validates the HMAC over the request, then uses the *unauthenticated* `request.topic` to select the handler and passes `request.shop` straight into `WebhookMetadata`, which the app is expected to trust as the tenant identity for the payload: [3](#0-2) 

`Utils::HmacValidator.validate` simply recomputes the signature from `to_signable_string` (the body) and compares it to the `hmac` header — it never authenticates `shop` or `topic`: [4](#0-3) 

Because the identity binding `hmac == HMAC(secret, body ‖ shop ‖ topic)` does not hold — the gem only checks `hmac == HMAC(secret, body)` — an attacker who possesses one legitimately-signed webhook delivery (e.g. by operating their own Shopify test store that installs the same app, or intercepting one delivery to any tenant) can capture `(raw_body, hmac)` and replay it to the app's webhook endpoint with a *different* `shopify-shop-domain` header (and/or a different `shopify-topic` header, as long as the JSON body happens to satisfy the target handler). Since the HMAC only covers the body, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` will dispatch the payload to the handler for the attacker-chosen topic, tagging it with the attacker-chosen `shop` value in `WebhookMetadata`.

### Impact Explanation
This breaks the cross-tenant boundary the gem's webhook verification is supposed to enforce: `shop` is the field host applications rely on to scope data writes/lookups to the correct tenant (e.g. "which merchant does this `orders/create` event belong to"), yet it is delivered outside the authenticated envelope. An attacker who can obtain any one valid `(body, hmac)` pair for the shared app secret (trivial if the attacker installs the app on their own store, since HMAC key is per-app not per-shop) can forge deliveries that Registry.process will accept as coming from an arbitrary `shop`/`topic` combination it never actually signed for that tenant, enabling cross-tenant data confusion in the host application. This matches the report's "Critical - cross-tenant access" category, since the identity that downstream code trusts (`shop`) is unauthenticated.

### Likelihood Explanation
Exploitability requires only network access to the app's public webhook endpoint and one legitimately-signed webhook body for the app (easily obtained by installing the same public app on an attacker-owned development store, which is normal, unprivileged behavior — no leaked secrets or privileged access needed). The `Registry.process` code path used by this gem is directly reachable and trusts `request.shop`/`request.topic` after only a body HMAC check, so likelihood is high for any app that relies on `WebhookMetadata#shop` for tenant scoping without independently re-validating it.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or the full raw header set Shopify signs against, if any is available) in the signed/verified material, or otherwise cryptographically bind them before dispatch — e.g. require the caller to also confirm `shop` against a known/expected value per delivery endpoint, or extend `to_signable_string` to incorporate the headers Shopify guarantees came from the same signed delivery. At minimum, document that `WebhookMetadata#shop`/`#topic` are unauthenticated and must not be trusted for tenant-scoping decisions without further verification.

### Proof of Concept
1. Attacker creates a free/dev Shopify store and installs the target app (same `client_secret`/api_secret_key is used for HMAC across all shops that install the app).
2. Attacker triggers a webhook delivery (e.g. `orders/create`) to capture a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair.
3. Attacker resends this exact `raw_body` and `hmac` header to the victim app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches, so `Registry.process` proceeds.
5. `Registry.process` dispatches to the handler using the attacker-controlled `topic` header and builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, which the host app's handler will treat as an authentic event for `victim-shop`, despite the payload/topic combination never having been signed for that shop.

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
