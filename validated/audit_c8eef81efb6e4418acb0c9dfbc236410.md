Confirmed. The `Registry.process` method only validates the HMAC over the raw request body (via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` → `@raw_body`), while the `shop` value dispatched to the handler is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never part of the signed bytes.I have enough to finalize the analysis.

### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` value that is handed to the app's handler is read from an HTTP header that is never included in the signed bytes. An attacker who can obtain one validly-signed webhook payload (e.g., by installing the app on their own store and receiving a legitimate webhook) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value, causing the app's webhook handler to process attacker-controlled data under a victim shop's identity.

### Finding Description
`Registry.process` validates a webhook via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For webhook `Request` objects, `to_signable_string` returns only the raw body: [3](#0-2) 

Meanwhile, `shop` is parsed directly from an unauthenticated HTTP header, completely disjoint from the signed bytes: [4](#0-3) 

After successful HMAC validation, this header-derived `shop` value is forwarded verbatim into `WebhookMetadata` and passed to the app's registered handler: [5](#0-4) [6](#0-5) 

This breaks the identity binding: `shop authenticated by HMAC == shop used to select/act on tenant data`. In reality, only `raw_body` is authenticated by the HMAC; the `shop` field acted upon by the handler is completely uncovered by the signature. Any HTTP client that can produce (or replay) a `(raw_body, hmac)` pair valid for the shared `client_secret` — trivially obtainable by installing the app on an attacker-owned development store and capturing one of its own legitimate webhook deliveries — can resend that same body/HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to any victim shop domain. `Registry.process` will accept it as authentic (the HMAC check only verifies the body was signed by Shopify with the correct secret, not which shop it was signed for) and dispatch it to the handler tagged with the attacker-chosen `shop`.

### Impact Explanation
Webhook handlers in a typical host application use `data.shop` to look up which merchant record/session to update (e.g., processing `app/uninstalled`, `shop/redact`, `customers/redact`, or business-data webhooks tied to that shop). Since the shop identity is forgeable independent of the HMAC, an attacker can inject events that are processed as if they originated from a victim shop, causing cross-tenant data corruption or triggering privileged flows (like uninstall/redact handling or a data-mutating webhook) against a shop the attacker does not control. This satisfies the Critical impact category of cross-tenant access, since the trust boundary between distinct merchant tenants is broken via a spoofable, unauthenticated identity field.

### Likelihood Explanation
Likelihood is realistic for any developer/attacker who can install the target app on their own (even free development) Shopify store: they receive genuinely signed webhooks for their own shop and can immediately replay the identical body+HMAC with a modified shop header value, without needing the `client_secret`, an access token, or any privileged access — matching the "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` identity into the authenticated material before dispatching to the handler: verify that the `shop` header value corresponds to a shop the application actually has an active installation/session for (looked up independently, not merely trusted from the header), and/or require the host application to cross-check `webhook_id`/`shop` against Shopify's Admin API before trusting it. At minimum, document prominently that `request.shop` is unauthenticated and must never be used to select a tenant/session without additional verification, and consider deriving/confirming shop identity from a source cryptographically tied to the signed payload where the webhook delivery format allows it.

### Proof of Concept
1. Attacker installs the target Shopify app on an attacker-owned store `attacker.myshopify.com` and lets a webhook (e.g., `orders/create`) fire to the app's endpoint, capturing the full request: `raw_body`, and headers `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only — this matches since `raw_body` and `hmac` are unchanged — so validation succeeds: [7](#0-6) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes it as a legitimate event for the victim tenant, even though the payload was never generated by or for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
