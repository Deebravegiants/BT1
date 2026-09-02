### Title
Webhook shop-domain identity spoofing via HMAC that only covers the request body, not the `shopify-shop-domain` / `topic` headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its `to_signable_string` from only the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from headers that are never included in the signed payload. `Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) as authenticated identity when constructing `WebhookMetadata` for the handler. This breaks the intended binding: `hmac == HMAC(secret, body)` is verified, but the code treats it as if `hmac == HMAC(secret, body + shop + topic)`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled directly from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `to_signable_string` (i.e., the body) as shown in `HmacValidator.validate_signature`: [3](#0-2) 

After that check passes, `Registry.process` immediately hands `request.shop` (and `request.topic`) to the app's handler as trusted, authenticated metadata: [4](#0-3) 

Because the HMAC signature is computed over the JSON body bytes alone, an attacker who has legitimately received one real webhook for their own store (any merchant can trigger webhooks for events on their own shop, e.g. by placing an order) possesses a body+HMAC pair that is valid for that exact body. Since the header `x-shopify-shop-domain` (or the new `shopify-shop-domain` header) sits outside the signed bytes, that attacker can replay the exact same body and HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value — e.g., a victim shop's domain — and `Utils::HmacValidator.validate` will still return `true`, because it only checks that the HMAC matches the body, never that it matches the claimed shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the app's webhook handler receives `WebhookMetadata#shop` (and `#topic`) as if Shopify had verified that value, when in fact the gem never binds the shop/topic to the HMAC. Any downstream logic in the host application that keys off `WebhookMetadata#shop` (session lookup, per-tenant data writes, per-tenant token usage) can be tricked into associating the replayed payload with the wrong tenant, since the library presents it as verified. This matches the report's bug class — an equality check that verifies the wrong bytes (body) while the field actually consumed downstream (shop) is unauthenticated — producing a cross-tenant confusion.

### Likelihood Explanation
Requires the attacker to be a legitimate, if malicious, holder of a real (shop, body, HMAC) triple — obtainable by any merchant installing the app and generating an event on their own store, or by anyone who can otherwise capture one valid webhook delivery. No secret material is needed; the attack only requires header manipulation on replay, which is straightforward for any client sending an HTTP POST to the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic) to the signature verification: include the `shop-domain` (and `topic`) header values in the string that is HMAC-verified, or independently verify the shop against a value already associated with the specific webhook/HMAC via Shopify's official verification guidance, rather than trusting the header as-is once the body-only HMAC passes. At minimum, document to consumers that `WebhookMetadata#shop`/`#topic` are not covered by the HMAC and must not be treated as authenticated without additional binding (e.g., cross-checking against the shop domain the app has on record via webhook_id or session).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real webhook event (e.g. `orders/create`), capturing the legitimate request: raw body `B`, and the real `x-shopify-hmac-sha256` header `H = HMAC_SHA256(secret, B)` sent by Shopify.
2. Attacker POSTs to the app's webhook endpoint with the identical body `B` and identical `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally forges `x-shopify-topic` similarly).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate(request)` recomputes HMAC only over `B`, matches `H`, and returns `true`. [5](#0-4) 
4. `Registry.process` proceeds to call the app's handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is `"victim-shop.myshopify.com"` — a value the app never independently verified as belonging to that HMAC. [6](#0-5) 
5. Any host application logic that trusts `data.shop` for tenant-scoped operations (writing per-shop data, looking up per-shop sessions/tokens) now operates under the wrong tenant identity, using attacker-controlled body content believed to originate from the victim shop.

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
