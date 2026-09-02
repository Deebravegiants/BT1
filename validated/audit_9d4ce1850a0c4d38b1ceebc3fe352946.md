### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds the value forwarded to the app's webhook handler (`shop`) from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header, but the HMAC validation performed by `Utils::HmacValidator` only covers the raw request body, never the shop header. This breaks the identity binding `shop_authenticated == shop_delivered_to_handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from the `shop-domain` header, independently of the signed bytes: [2](#0-1) 

`Registry.process` verifies the HMAC and then trusts `request.shop` when constructing the metadata handed to the app-provided handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the body for webhooks) and compares it to the `hmac-sha256` header value; it never incorporates `shop`, `topic`, `api_version`, or `webhook_id`: [4](#0-3) 

Because of this, the equality that should hold — `shop bound inside the HMAC == shop delivered to handler` — does not hold. Only `raw_body` is bound; the `shop-domain` header travels unauthenticated alongside it.

### Impact Explanation
Any entity that has obtained one valid `(raw_body, hmac-sha256)` pair for this app's webhook secret (e.g., a legitimate, unprivileged merchant who has installed the app and can observe/capture the raw POST their own shop's webhook delivery generates) can replay that exact body and HMAC to the same webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim tenant's domain). `Utils::HmacValidator.validate` will still return `true` because the signature check only depends on `raw_body`. `Registry.process` will then invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, while the HMAC only proves the body was signed for "some shop of this app," not for the shop claimed in the header. Downstream app code that uses `shop` from `WebhookMetadata` to look up per-tenant session/access-token state (the intended, documented use of this field) can be tricked into processing data under, or against, another tenant's identity — a cross-tenant access/data-integrity violation, since the shop binding it relies on was never authenticated by this gem.

### Likelihood Explanation
Exploitability requires the attacker to possess at least one genuine `(body, hmac)` pair produced by Shopify for this app (trivially obtainable by any merchant who installs the app, since Shopify sends real webhooks to installed apps' endpoints for ordinary events they trigger themselves). No knowledge of `client_secret`, access tokens, or any other credential is required — only a captured webhook delivery and the ability to POST to the app's public webhook endpoint with a modified header. This is realistically reachable by any unprivileged existing installer of the app, satisfying the "unprivileged internet user" bar.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable payload used for HMAC verification (or otherwise cryptographically bind the shop-domain header to the signed body, e.g., by re-deriving/confirming shop identity from a source that is itself authenticated), so that `Utils::HmacValidator.validate` fails if any of these header values are altered relative to what was actually signed by Shopify for that specific delivery.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook event (e.g., `orders/create`) that the app has registered a handler for.
2. Attacker captures the raw POST: body `B`, and header `X-Shopify-Hmac-Sha256: H` (valid, computed by Shopify using the app's real secret over `B`), along with `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the identical request to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (all other headers/body unchanged, including the still-valid `H`/`B` pair).
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only, matches `H`, returns `true` — the forged request passes signature validation as shown in `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, as shown in `lib/shopify_api/webhooks/registry.rb:188-199`, causing the app's business logic to run under the attacker-chosen (victim) tenant identity despite the request never actually originating from Shopify for that tenant.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
