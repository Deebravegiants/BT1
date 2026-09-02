## Analysis Result

### Title
Webhook shop/topic identity spoofing via unsigned headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and are never part of the signed material. `Registry.process` dispatches to a handler and constructs `WebhookMetadata` using these unsigned header values after checking only that the *body* HMAC is valid. This breaks the identity binding: `HMAC-valid == body originated from Shopify for the shop asserted in headers`, when in fact the HMAC only proves `body originated from Shopify for *some* shop that legitimately triggered this exact payload`.

### Finding Description
`Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the body: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (the body) against the `hmac` header: [3](#0-2) 

`Registry.process` trusts the header-derived `request.shop` and `request.topic` for dispatch and metadata construction immediately after this body-only check passes: [4](#0-3) 

Because a shop owner has full, legitimate control over their own store's data (order contents, customer fields, product titles, etc.), an unprivileged attacker who merely installs the app on their own (attacker-controlled) shop can generate a stream of genuinely Shopify-signed webhook bodies with attacker-chosen content. Since the `shop-domain`, `topic`, and `webhook-id` headers carry no HMAC coverage, the attacker can replay one of these bodies to a multi-tenant app's shared webhook endpoint while substituting an arbitrary `shop-domain` header (a victim shop) and/or `topic` header. `HmacValidator.validate` still succeeds (it never inspects the headers), so `Registry.process` will invoke the handler believing the event legitimately originated from the victim shop.

### Impact Explanation
This breaks the equality the gem is expected to enforce: `shop asserted in webhook metadata == shop actually authenticated by Shopify's signature`. Any app relying on this gem's webhook flow to key per-tenant behaviour (e.g., looking up a stored session/access token by `WebhookMetadata#shop`, updating tenant-scoped records, or triggering follow-up Admin API calls using the victim shop's session) can be made to act on attacker-controlled data under a victim tenant's identity — a cross-tenant confused-deputy condition, meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Requires only an unprivileged Shopify shop (attacker installs the target app on their own store, which is possible for any public app, or simply captures one legitimate webhook delivery they already receive) and network access to the app's shared webhook endpoint. No secrets, tokens, or privileged accounts are needed — only the ability to modify HTTP headers of an otherwise genuinely-signed request, which is trivial for any actor capable of sending arbitrary HTTP requests.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` in the HMAC-signable string (or otherwise cryptographically bind them, e.g. by deriving them from a signed payload field rather than headers), so that `Utils::HmacValidator.validate` fails if any of these identity-bearing headers are altered relative to what Shopify actually signed for that request.

### Proof of Concept
1. Attacker installs the target embedded app on their own shop `attacker.myshopify.com` and triggers a real event (e.g. `orders/create`) with attacker-chosen order fields. Shopify delivers a genuine webhook: body `B`, headers `x-shopify-hmac-sha256: H(B)`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker resends the identical body `B` and `hmac` header to the app's shared webhook endpoint, replacing the `shop-domain` header with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the spoofed headers; `Utils::HmacValidator.validate` computes `HMAC(secret, B)`, which still matches `H(B)` — validation passes. [5](#0-4) 

4. `Registry.process` dispatches to the `orders/create` handler with `WebhookMetadata#shop == "victim.myshopify.com"` and attacker-controlled `body`, even though `victim.myshopify.com` never sent this event.

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
