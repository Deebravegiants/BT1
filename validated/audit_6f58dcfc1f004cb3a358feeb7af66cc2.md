### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used for tenant attribution purely from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while `Utils::HmacValidator.validate` only checks the HMAC against the raw request body. This breaks the binding `hmac-authenticated bytes == bytes used to identify the tenant`, mirroring the reported bug class where a field acted on by application logic (`workingSupply`) was not kept consistent with the field that was actually verified/accumulated (`totalBoost`).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the header, entirely independent of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the body only) and then forwards `request.shop` verbatim into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [3](#0-2) 

The HMAC secret (`Context.api_secret_key` / `client_secret`) is a single, app-wide secret shared across *every* shop that has installed the app — it is not shop-specific: [4](#0-3) 

Because the signature only binds the body, not the shop header, `hmac_valid(body, secret) == true` does **not** imply `shop_header == shop_that_actually_sent_body`. Any two webhook deliveries produced with the same app secret produce cryptographically valid HMACs regardless of which header values accompany them. This is exactly the "field acted on but not covered by the HMAC" analog: the gem computes/verifies one thing (body integrity) but the host application is handed and expected to trust another, uncorrelated thing (`shop`) as if it had been verified together.

### Impact Explanation
An attacker who controls (or has previously captured) any one valid webhook body+HMAC pair issued by Shopify for the shared app secret (e.g., from their own installed test shop) can resend that exact body to the app's webhook endpoint while substituting a different `shopify-shop-domain` header value. `Utils::HmacValidator.validate` will still report the signature as valid because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to an arbitrary victim shop. Any host application that uses `WebhookMetadata#shop` to look up per-tenant session/access-token records or to scope data writes (a normal, documented usage pattern) can be made to process attacker-controlled data under another merchant's identity — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Reaching this requires only unauthenticated internet access to the app's public webhook endpoint plus possession of one legitimately-signed webhook body (trivially obtainable by installing the app on an attacker-owned development shop, which uses the exact same shared `client_secret`). No access token, leaked credentials, or privileged account is required, matching the "unprivileged internet user" threat model.

### Recommendation
Include the shop domain (and ideally webhook id/topic) inside the HMAC-signable payload, or otherwise cryptographically bind the `shop-domain` header to the request body before trusting it — e.g., verify the header value against a shop that the app already has an active, previously-authenticated session/install record for, rather than trusting it because "the body's HMAC happened to validate." At minimum, document prominently that `shop` in `Request`/`WebhookMetadata` is unauthenticated and must be independently cross-checked by host applications before being used for tenant scoping.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic; Shopify sends a request with a valid `x-shopify-hmac-sha256` computed from the shared `client_secret` and the JSON body.
2. Attacker captures `raw_body` and `hmac` from that delivery.
3. Attacker replays a POST to the app's webhook endpoint with the same `raw_body`/`hmac` but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), and `Utils::HmacValidator.validate(request)` returns `true` because it only hashes `@raw_body`.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the host app to attribute the attacker's payload to the victim tenant. [3](#0-2)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
