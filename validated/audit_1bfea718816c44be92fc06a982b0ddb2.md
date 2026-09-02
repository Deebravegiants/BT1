### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator` verifies binds only the *body*, never the `shop-domain` header. Yet `shop` is read straight from that unauthenticated header and handed to the app's webhook handler as the tenant identifier. Anyone who can obtain one validly-signed webhook (e.g. by installing the app on their own shop) can replay the identical `body`+`hmac` pair while substituting an arbitrary `shop-domain` header, and `Registry.process` will accept it as authentic for the victim shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. `Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string`: [2](#0-1) 
Meanwhile `Request#shop` is parsed from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely outside the signed material: [3](#0-2) 
`Registry.process` validates only the HMAC, then forwards `request.shop` unchanged into `WebhookMetadata`, which is passed to the app's handler as the shop identity for that event: [4](#0-3) 
`WebhookMetadata.shop` is a plain, unauthenticated `String` field: [5](#0-4) 

The identity binding that should hold is: `shop-domain header == shop that the HMAC-signed body actually originated from`. Because the HMAC only signs `@raw_body`, this equality is never checked — `HmacValidator.validate` returns `true` for *any* header set as long as the body+secret produce a matching digest, regardless of which `shop-domain` value accompanies it. The documented handler contract explicitly instructs apps to trust `data.shop` for per-shop dispatch (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), so this unauthenticated field routinely drives tenant-scoped logic (session/access-token lookup, per-shop record updates, `app/uninstalled` handling, etc.) in host applications built directly on this gem's documented API.

### Impact Explanation
An attacker who runs their own shop with the app installed receives genuine, correctly-signed webhooks from Shopify for their own shop (any topic, any body they can trigger, e.g. `orders/create`, `customers/update`, or `app/uninstalled`). The attacker captures the exact raw body and its valid `hmac-sha256` header, then POSTs that identical body+HMAC pair to the app's public webhook endpoint while swapping the `shop-domain` header to a victim shop's domain. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) validates successfully because the HMAC never depended on the header, and the handler receives `WebhookMetadata` claiming the event belongs to the victim shop. This is a cross-tenant identity confusion: attacker-controlled data (order/customer payloads, or even a forged `app/uninstalled` event) is processed by the app as if it originated from a different merchant's shop, with no need for the app's `client_secret`, an access token, or any privileged access — only a public webhook endpoint and a self-service shop install.

### Likelihood Explanation
Likelihood is high: the webhook endpoint is by design internet-reachable and unauthenticated beyond the HMAC; installing a development/trial shop to harvest one legitimately signed payload per topic is trivial and requires no special privileges; and the header-swap replay requires no cryptographic work at all since the secret is never involved in producing the `shop-domain` binding.

### Recommendation
Bind the tenant identity into the verified material. Either:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in `to_signable_string` so the HMAC covers them, or
- Cross-check `request.shop` against an independently-trusted source (e.g. re-derive/verify the shop via a signed API call, or require the app to only accept the shop values it has an active, previously-established session for) before dispatching to the handler, and document this requirement clearly since Shopify's own HMAC spec signs body only.

At minimum, update `docs/usage/webhooks.md` and the `WebhookMetadata#shop` contract to explicitly warn implementers that `data.shop` is not cryptographically authenticated and must not be trusted for tenant-scoped side effects without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. updates a product) to receive a legitimately signed payload:
   - `raw_body = '{"id":123,...}'`
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body under app's real secret>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
2. Attacker resends the exact same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook callback URL, replacing the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `raw_body` — validation succeeds.
4. The handler executes with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, causing the app to attribute attacker-controlled webhook content (or an uninstall event) to the victim shop's tenant context.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
