Based on the codebase analysis, there's a valid analog in this gem's webhook processing pipeline that mirrors the report's bug class: **a field acted on but not covered by the HMAC**.

### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) attribution is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields it exposes — and that `Registry.process` passes on to application handlers as authoritative tenant/routing data — come from unauthenticated HTTP headers that are never bound into that signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` HMACs exactly that string against `Context.api_secret_key`: [1](#0-0) [2](#0-1) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` (and equivalent) headers, with no cryptographic binding to the body they're paired with: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (and the other header-derived fields) to the app's handler as trusted tenant identity: [4](#0-3) 

The binding that should hold is:
`HMAC(raw_body, api_secret_key) valid` ⟺ `(shop, topic, webhook_id, api_version, body) all originated together from Shopify`

In reality the equality only covers `body`; `shop` (and the other headers) are outside the signed payload. An unprivileged internet user who controls **any** valid `(raw_body, hmac)` pair signed with the app's secret — trivially obtainable by installing the app on their own attacker-controlled shop and capturing one of their own legitimately delivered webhooks — can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g. a victim merchant's domain). `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` hands the handler a `WebhookMetadata` claiming the victim shop sent this payload.

### Impact Explanation
If the host application's webhook handler uses `data.shop` to look up the corresponding merchant's stored session/access token or to attribute/persist data (the intended and documented use of `WebhookMetadata#shop`), an attacker can inject data attributed to, or trigger shop-scoped side effects against, a tenant they do not control — a cross-tenant access/confusion vulnerability that rides on this gem's HMAC verification appearing to have validated the whole request when it only validated the body.

### Likelihood Explanation
Exploitation requires no secrets: the attacker only needs their own legitimate install of the target app (a normal unprivileged capability) to obtain one valid `(body, hmac)` pair, then a single crafted HTTP request with a forged shop header to any deployment of the app's public webhook endpoint.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cross-check the header-derived `shop` against a shop already known/authorized by the app (e.g. an existing stored session) before treating `WebhookMetadata#shop` as authoritative. At minimum, document in `Registry.process`/`Webhooks::Request` that only the body is HMAC-covered so integrators do not implicitly trust header fields as verified.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture one legitimately delivered webhook: raw body `B` and its valid header `x-shopify-hmac-sha256: H` (computed by Shopify over `B` with the app's real secret).
2. Send a POST to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid since it only signs `B`), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because it only recomputes HMAC over `@raw_body`.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, `webhook_id`/`topic`/`body` all attacker-influenced/forged, despite the request never having originated from, or been authorized by, that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
