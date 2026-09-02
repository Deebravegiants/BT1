### Title
Webhook HMAC signature only covers the request body, not the `shop-domain` header — allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC only against that body-only signable string. Consequently, the identity binding "the `shop` acted on by the webhook handler" is not covered by the cryptographic check that is supposed to prove the message's authenticity, exactly the class of bug described in the report (a field acted on but not covered by the HMAC).

### Finding Description
`Registry.process` authenticates an inbound webhook solely via: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For webhook requests, `to_signable_string` is defined as just the raw body: [3](#0-2) 

But `shop`, `topic`, `webhook_id`, and `api_version` — the values that are actually acted upon downstream — are all pulled from HTTP headers that are never part of the signed material: [4](#0-3) 

`process` then hands `request.shop` straight to the handler as the tenant identifier, with no additional binding to the signed body: [1](#0-0) 

Equality that should hold but does not:
`bytes_verified_by_hmac == "shop-domain" header value used to attribute the webhook to a tenant`

Before the request: HMAC covers `{raw_body}`; `shop`/`topic`/`webhook_id`/`api_version` are unauthenticated headers.
After the request: the handler receives `WebhookMetadata` keyed by an unauthenticated `shop` value, even though the HMAC check "passed."

### Impact Explanation
Any unprivileged internet user who is themselves a legitimate merchant/tenant on the app (i.e., can trigger a webhook of their own, thereby obtaining a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret for a topic with a fixed/predictable body, e.g. `shop/redact`, `customers/redact`, or any topic whose payload does not embed the shop domain) can replay that exact body+HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header to name a victim shop. Because the HMAC only proves the body was signed with the shared secret — not which shop or topic it belongs to — `Registry.process` will accept the forged headers as valid and invoke the handler with `shop: <victim shop>`. Any host application that uses `WebhookMetadata#shop` to key data writes/deletes (a documented, intended use of this field) will perform tenant-scoped actions attributed to the wrong shop, i.e., cross-tenant access/mutation using only the attacker's own legitimately-issued webhook credentials. This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any app that registers at least one webhook topic with a body that doesn't itself encode a shop identifier bound by the HMAC (many topics' payloads only contain resource IDs, not the shop domain). The attacker needs no secret, no privileged account beyond being an ordinary installed merchant, and no host application misuse — this is purely a gap in the gem's own `to_signable_string`/header design that host apps cannot fix without re-implementing HMAC validation themselves.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the signable/verified material, or otherwise cryptographically bind the `shop` header to the HMAC before exposing it via `WebhookMetadata`. At minimum, document/enforce that `request.shop` must not be trusted as a tenant key unless independently corroborated (e.g., cross-checked against the session's known shop), and consider verifying the header set as part of `HmacValidator.validate` for webhook requests specifically.

### Proof of Concept
1. App registers a webhook handler for topic `T` whose JSON body does not contain the shop domain (e.g. many `*/create` or `*/update` topics only include resource attributes).
2. Attacker, as a legitimate merchant of shop `attacker.myshopify.com`, triggers topic `T` in their own store, causing Shopify to send the app a real webhook with body `B` and header `x-shopify-hmac-sha256: H = HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same `B` and `H` directly via HTTP POST to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches `H` (body unchanged), so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`.
5. The host application, following the gem's documented contract, performs tenant-scoped logic keyed on `data.shop`, now operating against `victim.myshopify.com` using attacker-supplied data — a cross-tenant write/side-effect the attacker fully controls in content and timing.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
