### Title
Webhook `shop` (and `topic`) identity is read from unauthenticated HTTP headers that are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop` (and `topic`) values pulled from HTTP headers to build the `WebhookMetadata` that is handed to the host app's `WebhookHandler`. The header-derived `shop` value is never part of the signed payload, so the equality the library implicitly assumes — `hmac_valid(raw_body) ⇒ shop_header_is_authentic` — does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), while `to_signable_string` — the data actually fed into the HMAC check — returns only `@raw_body`.

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`: [2](#0-1) 

`Registry.process` verifies the HMAC and then immediately trusts `request.shop`/`request.topic` (both header-derived, unsigned) to construct the metadata passed to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is the field the host application is expected to use to identify which merchant/tenant the webhook belongs to: [4](#0-3) 

The identity binding that should hold is:
`bytes_verified_by_hmac == bytes_used_to_identify_the_tenant`

Here it does not: HMAC verifies only `@raw_body`; tenant identity (`shop`) comes from a header outside that scope. This mirrors the report's bug class — "a field acted on but not covered by the HMAC" — applied to this gem's webhook-processing code instead of Compound's liquidation logic.

### Impact Explanation
An unprivileged actor who can capture one legitimately-signed webhook body/HMAC pair for a topic (e.g., by installing the app on their own store and receiving a real webhook delivery, which is signed by Shopify using the app's real `client_secret` — something the attacker never needs to know) can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting a different `X-Shopify-Shop-Domain` header. Because `shop` is outside the signed scope, `HmacValidator.validate` still returns `true`, and `Registry.process` will invoke the host app's handler with `WebhookMetadata#shop` set to the attacker-chosen value. If the host application uses this `shop` field to route/attribute the payload to a merchant record (a documented, expected use of `WebhookMetadata`), this results in cross-tenant data being associated with the wrong shop — data belonging to shop A being processed/stored under shop B's identity. This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid signed webhook body for any topic (trivial for anyone who can install the target app on a store they control, since Shopify will deliver real signed webhooks to that installation), plus the ability to send an HTTP request to the app's public webhook endpoint with a forged shop header — both of which are within reach of an unprivileged internet user with no access to the app's `client_secret`, access tokens, or any privileged account.

### Recommendation
Include the shop domain (and ideally topic) in the signed material, or otherwise cryptographically bind them: e.g., verify the HMAC as currently done, but additionally require that the `shop` header corresponds to a shop with a valid stored session/access token before trusting it for routing, and/or extend `Request#to_signable_string` to incorporate the header value it uses for `shop` so a mismatch invalidates the signature. At minimum, document and enforce that host applications must cross-check `WebhookMetadata#shop` against an independently verified session store rather than trusting it as an authenticated tenant identifier.

### Proof of Concept
1. Attacker creates their own development store and installs the target Shopify app, subscribing to webhook topic `orders/create`.
2. Shopify delivers a legitimately HMAC-signed webhook to the app's endpoint: `raw_body = B`, `X-Shopify-Hmac-Sha256 = H`, `X-Shopify-Shop-Domain = attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` (their own traffic, no secret needed).
4. Attacker POSTs the same `B` and `H` to the app's webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(..., B)` against `H` — this still passes because `B` and `H` are untouched. [3](#0-2) 
6. The host app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store, demonstrating the broken shop⇔signature binding.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
