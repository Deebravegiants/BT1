### Title
Webhook `shop-domain` (and `topic`, `webhook-id`) are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body. The `shop`, `topic`, and `webhook_id` values used downstream to identify which tenant/shop the event belongs to are read from HTTP headers that are never part of the signed payload, so they carry no cryptographic binding to the HMAC-validated body.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop`, `topic`, `webhook_id` are pulled straight from unauthenticated headers: [2](#0-1) 

`Utils::HmacValidator.validate_signature` recomputes the HMAC over `verifiable_query.to_signable_string` (i.e. body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authenticating the whole request, then builds `WebhookMetadata` using the unauthenticated `request.shop` header: [4](#0-3) 

The identity binding the code implicitly assumes is:
`hmac_valid(raw_body) == tenant_is(shop_header)`

but the actual guarantee provided is only `hmac_valid(raw_body) == body_came_from_holder_of_api_secret_key`. The `shop-domain` header is never part of the signed material, so nothing prevents an attacker from taking any previously-observed, validly-signed `(raw_body, hmac)` pair — for example one delivered to their own shop's webhook — and replaying it to the same public webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header rewritten to a different, victim shop that uses the same app. `Registry.process` will pass HMAC validation (body/HMAC pair is genuinely valid) and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop, breaking the shop-authenticated-versus-shop-used binding.

### Impact Explanation
This is a cross-tenant integrity/confidentiality break: a party who can obtain one legitimately-signed webhook body (e.g. by triggering a webhook for their own shop) can cause the app to process that payload under an arbitrary other shop's identity, without needing `api_secret_key`, an access token, or any privileged credential. Depending on what the host app's webhook handlers do with `WebhookMetadata#shop` (e.g. write order/inventory data, cancel subscriptions, revoke access, trigger uninstall cleanup) this can corrupt or leak another merchant's tenant data — matching the Critical "cross-tenant access" impact class.

### Likelihood Explanation
The webhook endpoint is a public, unauthenticated HTTP endpoint by design (protected only by the HMAC check in this gem). Any actor who is themselves a merchant using the app (i.e., who legitimately receives at least one webhook for their own shop) can capture a valid `(body, hmac)` pair and replay it with a forged shop header, since nothing else on the wire needs to be attacker-controlled or guessed — the HMAC and body are reused verbatim. This requires only network access to the shared webhook endpoint, no secret material.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material verified against the HMAC, or otherwise cryptographically/logically tie the header-derived `shop` value to the signed body before it is trusted:
- Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification, or
- After HMAC validation, independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation for this app (not just header presence) before dispatching to handlers, and reject if the raw body's shop-scoped identifiers (if present, e.g., an included `myshopify_domain` field in body) don't match the header.

### Proof of Concept
1. Attacker installs the target app on Shop A and performs an action that triggers a real webhook (e.g. `orders/create`). Shopify delivers to the app's endpoint:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid HMAC of raw body>`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`
   - Body: `{"id": 123, ...}` (raw bytes captured by the attacker, who is the legitimate recipient/owner of Shop A).
2. Attacker replays the exact same body and `X-Shopify-Hmac-Sha256` value to the same app webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (unmodified) body against the (unmodified) HMAC: [5](#0-4) 
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <Shop A's data>, ...)`, causing the host app to act as if the order belonged to `victim-shop`, corrupting/leaking cross-tenant data.

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
