Confirmed: `Registry.process` passes `request.shop` (from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header) directly to the handler as the tenant identifier [1](#0-0) , while the HMAC verification only covers `@raw_body` and never binds the `shop` header [2](#0-1) .

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Registry.process` validates the request by running `Utils::HmacValidator.validate(request)` against that body-only signable string. The `shop` (`shopify-shop-domain`/`x-shopify-shop-domain`) header, `topic`, `webhook-id`, and `api-version` headers are never part of the signed material. The `shop` value taken from this unauthenticated header is then handed straight to the app's webhook handler as the tenant identifier.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the caller-supplied `hmac` [3](#0-2) . For webhook requests, `to_signable_string` is defined as just `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers with no cryptographic binding to the signature [4](#0-3) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching, then builds `WebhookMetadata` using `request.shop` taken straight from the unauthenticated header [1](#0-0) .

This breaks the intended identity binding: `shop-domain header == shop whose body the HMAC actually authenticates`. Because every shop installed on a multi-tenant app shares the same app-level `api_secret_key`, a merchant who has legitimately installed the app (and therefore legitimately receives valid, correctly-HMAC'd webhooks for their own shop) can capture one of their own genuine webhook deliveries — the raw body plus its valid `hmac-sha256` header stays untouched and valid — and simply replace the `shopify-shop-domain` header value with a different tenant's shop domain before resubmitting it to the app's webhook endpoint. Since the signature only covers the body, and topic/shop are not included in the signed payload, the forged request still passes `HmacValidator.validate`, and the app processes it believing it originates from the victim shop.

### Impact Explanation
This is a cross-tenant data/authorization confusion: an app receiving this forged webhook will act on data (e.g., `customers/redact`, `orders/create`, `app/uninstalled`, etc.) under the identity of a shop the attacker doesn't own. Depending on what the host application does with `WebhookMetadata#shop` (e.g., looking up/deleting a session, updating billing state, disabling access, replaying data as if it came from another merchant), this can lead to cross-tenant state corruption using only the attacker's own legitimately-received webhook traffic — no access to `api_secret_key`, tokens, or the target shop's own credentials required.

### Likelihood Explanation
Reachable by any unprivileged merchant who has installed the app: they naturally receive real webhooks (with valid HMACs) for their own shop and only need to replay the raw body + valid HMAC header while swapping the `shop-domain` header. No secrets are needed since the HMAC itself is untouched.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) claim in the signed material, or otherwise cryptographically bind the shop identity to the payload before trusting `request.shop` in `Registry.process`/handlers. At minimum, document that host applications must not treat the un-authenticated `shop-domain` header as trustworthy without additional verification (e.g., cross-checking against a known/installed shop list) — but since this gem is the one parsing and exposing `shop` as part of `WebhookMetadata`, the binding should be enforced at this layer, e.g. by making `to_signable_string` incorporate the shop/topic headers or by exposing a dedicated “verified shop” separate from raw header access.

### Proof of Concept
1. App installs Shopify app on shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. for `customers/redact`, with headers:
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <valid HMAC over raw body>`
   - `X-Shopify-Topic: customers/redact`
   and raw JSON body `B`.
2. Attacker resends this exact body `B` and the exact same valid `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `to_signable_string` returns `B` unchanged [2](#0-1) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` and matches the attacker-supplied (still valid, since `B` is unmodified) HMAC [5](#0-4) .
5. Validation passes; the handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now returns `"victim.myshopify.com"` [6](#0-5) , causing the host application to act on the victim shop's tenant context despite the payload actually belonging to the attacker's own shop.

### Citations

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
