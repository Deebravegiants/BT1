### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) exclusively from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC integrity check computed by `HmacValidator` only covers the raw request body. Any host application that trusts `WebhookMetadata#shop` (delivered by `Registry.process`) to identify which tenant/merchant a webhook event belongs to is exposed to cross-tenant spoofing, because the header carrying that identity is never part of the signed bytes.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and exposes: [1](#0-0) 
`hmac` and `shop` are both read from headers, but `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` — i.e., the body — and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` only checks this body-HMAC, then immediately trusts `request.shop` to build the metadata dispatched to the host application's handler: [4](#0-3) 

The identity equality the gem is implicitly claiming is:
`HMAC-verified(raw_body) == HMAC-verified(shop-domain-header)`

but the actual check performed is only `HMAC-verified(raw_body)`. The `shop` field flows unauthenticated into `WebhookMetadata#shop`: [5](#0-4) 

This is a byte-scope mismatch: bytes verified (body only) vs. bytes the application acts on (body + shop header) — one of the accepted analog patterns (identity field acted on but not covered by the HMAC).

### Impact Explanation
Because the `api_secret_key` used to compute the webhook HMAC is shared across every shop that has installed the app (it is the app's own client secret, not a per-shop secret), any merchant who has legitimately installed the app receives their own valid `(raw_body, hmac)` pairs from real Shopify webhook deliveries. That merchant can replay one of their own legitimately-signed webhook bodies to the app's webhook endpoint while altering only the `x-shopify-shop-domain` header to name a different, victim shop. `HmacValidator.validate` still succeeds (it never examined the header), and `Registry.process` dispatches a `WebhookMetadata` claiming to originate from the victim shop. If the host application uses this `shop` value to key writes, invalidate/create records, trigger app-side actions, or attribute billing/webhook-driven events to a shop (a documented and expected use of `WebhookMetadata#shop`), an attacker-controlled shop can inject events attributed to another tenant — a cross-tenant boundary violation performed entirely with information the attacker already legitimately possesses (no `api_secret_key`, access token or other privileged secret is required beyond what any app-installing merchant already receives).

### Likelihood Explanation
Medium-High: exploitation requires no leaked credentials — only that the attacker be (or control) any shop that has installed the target app, which is trivial for public/free apps. They passively capture one authentic webhook delivery (body+HMAC) for their own shop and replay it with a modified shop header to the app's public webhook endpoint. The library does nothing to prevent this because `shop` is architecturally outside the HMAC's coverage.

### Recommendation
Extend HMAC coverage (or add a secondary binding check) so that the asserted shop identity cannot be swapped independently of the signed payload:
- Bind the `shop` header into the signable string used by `HmacValidator`, e.g., have `Webhooks::Request#to_signable_string` include the shop-domain header alongside the raw body (matching Shopify's actual webhook HMAC scheme, which is computed purely over the raw body but is only valid in combination with the endpoint being provisioned per-shop context) — at minimum, document and enforce in `Registry.process` that the `shop` value must be cross-checked against an out-of-band trusted source (e.g., an active, previously-stored session/access-token record for that shop) before being trusted for any privileged action, rather than treated as authenticated solely because the body HMAC passed.
- Reject webhook requests whose `shop` header does not correspond to a shop with a known valid app installation/session, closing the replay-with-relabeled-shop vector.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g., `orders/create`) that Shopify delivers with headers `x-shopify-hmac-sha256: <valid-hmac>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and some JSON body `B`.
2. Attacker captures the raw body `B` and its accompanying valid `hmac`.
3. Attacker replays a POST to the app's webhook endpoint with the identical raw body `B` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) and matches the supplied `hmac` — validation succeeds: [4](#0-3) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, attributing the attacker-controlled webhook body to the victim shop, even though `victim-shop.myshopify.com` never sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
