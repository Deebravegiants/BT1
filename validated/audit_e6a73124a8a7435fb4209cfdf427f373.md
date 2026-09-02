### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but only binds the raw request body to the HMAC signature. The `shop` domain (and `topic`, `api_version`, `webhook_id`) are read from unauthenticated HTTP headers and passed straight through to the application's webhook handler as the tenant identity, without being covered by the signature that `HmacValidator` checks.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to that value: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC only over `verifiable_query.to_signable_string`, i.e. only the body: [3](#0-2) 

`Registry.process` accepts the request once that body-only HMAC check passes, then dispatches the handler using the unauthenticated `request.shop` value as the tenant identifier: [4](#0-3) 

The identity binding broken is:
`shop authenticated by HmacValidator` ≠ `shop delivered to the host application's handler (WebhookMetadata#shop)`.

Because the HMAC only covers the body, any valid `(raw_body, hmac)` pair — including one an attacker legitimately obtains for their own registered shop (e.g. by triggering an event such as `products/create` on a shop they control, which is a shop for which they are a fully authorized, unprivileged actor with respect to this gem) — remains cryptographically valid when the `shop-domain` header (and `topic`/`webhook-id`/`api-version`) are swapped to name a different, victim shop. `Utils::HmacValidator.validate` will still return `true`, since it never inspects `shop`, and `Registry.process` will invoke the app's webhook handler believing the (attacker-controlled) body originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-confusion primitive: an unprivileged internet user who merely controls one shop (or intercepts/replays one delivered webhook) can cause the host application to process attacker-controlled webhook data under a different, arbitrary shop's identity. Any host application that relies on `WebhookMetadata#shop` (as documented/returned by this gem) to select which tenant's data to update will be attributing forged data to the wrong tenant — a direct cross-tenant access/data-integrity violation performed entirely without possession of `api_secret_key` or any access token.

### Likelihood Explanation
The attack requires no secret material: `raw_body` and its HMAC are attacker-obtainable from any real webhook delivered to a shop the attacker controls; only the headers (which are not covered by the signature) need to be modified before replay to the app's webhook endpoint. `Utils::HmacValidator` and `Webhooks::Registry.process` will accept the forged request unconditionally, since shop/topic/webhook-id are outside the signed content.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string used for HMAC verification (or otherwise cryptographically bind them to the payload), so `HmacValidator.validate` fails if any of these identity fields are altered relative to what Shopify actually signed. At minimum, document and enforce that the consuming application must cross-check `request.shop` against its own registered subscription state rather than trusting it as authenticated by this gem's HMAC check.

### Proof of Concept
1. Attacker owns/operates `attacker-shop.myshopify.com` and registers a webhook (e.g. `products/create`) pointing at the target app's shared webhook endpoint (the same endpoint used for all merchants).
2. Attacker triggers the event on their own shop with attacker-controlled body content, capturing the genuine `raw_body` and the corresponding `x-shopify-hmac-sha256` value that Shopify computed with the app's real `api_secret_key`.
3. Attacker resends the identical `raw_body`/HMAC pair to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and, if desired, `x-shopify-topic`/`x-shopify-webhook-id`).
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over `raw_body` only — it matches, so validation succeeds.
5. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker-controlled data> ...)`, causing the host application to act on forged data under the victim shop's identity.

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
