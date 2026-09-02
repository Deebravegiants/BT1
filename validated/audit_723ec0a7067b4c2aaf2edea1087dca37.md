### Title
Webhook shop-domain header is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (tenant), `topic`, and `webhook_id` fields used to route and attribute the webhook are read straight from unauthenticated HTTP headers that are never included in the signed material. Any party able to produce (or replay) a validly-signed body/HMAC pair for the shared app secret can attach an arbitrary `shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and dispatch it to the handler attributed to that spoofed shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are pulled directly from HTTP headers, which are entirely outside the signed content: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC only against `to_signable_string` (i.e., the body), using the app's single, shop-independent `api_secret_key`: [3](#0-2) 

`Registry.process` trusts `request.shop` for attribution as soon as the (body-only) HMAC check passes, with no separate binding between the signed body and the shop header: [4](#0-3) 

The identity binding that is broken is: `hmac_valid(raw_body, api_secret_key) == true` is treated as equivalent to `shop_header == originating_shop`, but the header is never part of the HMAC input, so these two facts are logically independent. Because `api_secret_key` is shared by the app across every installed shop (it is not per-tenant), a body+HMAC pair that is valid for shop A's webhook delivery remains a valid HMAC for any other header combination, including a `shopify-shop-domain` header claiming shop B. An attacker who controls shop A (a legitimate but malicious merchant of a multi-tenant app) can capture one of their own genuine webhook deliveries (body + `x-shopify-hmac-sha256`) and resend it to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop, without needing the `api_secret_key` itself — only a previously observed valid body/HMAC pair for their own tenant.

### Impact Explanation
This crosses a tenant boundary: data belonging to the attacker's own shop (order, customer, etc. payloads they legitimately received) can be replayed and processed by the app as if it originated from a different merchant's shop. Any downstream logic that keys persistence, entitlements, or side effects off `WebhookMetadata#shop` will store or act on attacker-supplied data under the victim's tenant identity, which is a cross-tenant access/data-integrity issue as defined in scope.

### Likelihood Explanation
The attacker needs no privileged credentials, no `api_secret_key`, and no TLS interception of the victim — only their own valid app installation and a single observed webhook body+HMAC from their own tenant, plus knowledge of the app's public webhook endpoint. This is achievable purely as an "unprivileged internet user"/merchant of the app.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material, or otherwise cryptographically tie the header-derived shop to the authenticated request (e.g., verify the shop header against a per-shop registered webhook secret/state, or include the shop domain in the HMAC computation) rather than trusting a header that sits entirely outside the HMAC boundary.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook event (e.g., creates an order), receiving from the app's server logs/proxy the raw body `B` and header `x-shopify-hmac-sha256: H` (valid since `H = HMAC_SHA256(api_secret_key, B)`).
2. Attacker sends a forged HTTP request to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim.myshopify.com` and any desired `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds because `B` and `H` are unchanged. [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the attacker's own webhook payload to be processed and stored under the victim shop's identity.

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
