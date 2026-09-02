### Title
Webhook HMAC signature covers only the raw body, not the `shop-domain` header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `Utils::HmacValidator.validate` authenticates the body bytes but never binds the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers to that signature. `Registry.process` trusts `request.shop` (parsed straight from the unauthenticated header) as the tenant identifier passed to the application's webhook handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `#shop` is read directly from the `shop-domain` header, independent of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac`: [3](#0-2) 

Since `to_signable_string` is just `@raw_body`, the signature check only proves the *body* bytes are authentic for *some* legitimate webhook delivery — it proves nothing about which shop the delivery is attributed to. `Registry.process` then forwards this unauthenticated `shop` value straight to the application handler as the tenant identifier: [4](#0-3) 

This breaks the intended identity binding: `verified(body) == verified(shop)` is assumed by callers, but only `verified(body)` actually holds; `shop` is `parsed(header)`, never `verified(header)`.

This is directly analogous to the referenced report's bug class: a field that is acted upon by the application (there, the deposited/withdrawn gas token; here, the shop/tenant attribution) is not covered by the same authentication mechanism (there, deposit vs. withdraw mismatch; here, HMAC signs body but not shop header), so the trusted computation diverges from what was actually verified.

### Impact Explanation
An unprivileged holder of any one legitimate, unmodified `(raw_body, hmac)` pair for a webhook topic (e.g. a merchant who has the app installed on their own shop and can observe/capture webhooks Shopify delivers to their own endpoint) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass because it only re-hashes `raw_body`. The application's handler then executes tenant-scoped logic (e.g., `shop/redact`, `customers/data_request`, `customers/redact`, or any custom `Http` registration's `handler.handle`) believing the event originated from the victim shop specified in the forged header, producing cross-tenant data confusion/action — the "High: cross-tenant access" class of impact, since one tenant's authenticated event content can be reattributed to another tenant's identity.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to possess at least one genuine, unmodified `(body, hmac)` pair for the target app (trivially available to any merchant who installs the app and receives normal webhook traffic to their own endpoint, or intercepts one in transit to a non-TLS-enforced test endpoint), and requires the host application to trust `request.shop`/`WebhookMetadata#shop` as the tenant key without independent cross-validation — which is exactly the documented, intended usage pattern shown by `Registry.process`.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the signed material, or otherwise cryptographically bind them to the raw body before verifying — e.g., have `to_signable_string` mix in the normalized `shop-domain` header, or require the consuming application to independently verify that `shop` corresponds to a shop actually associated with the delivered `webhook_id`/topic via a separate authenticated lookup (e.g., confirming the shop has an active, matching Shopify subscription for that webhook id) rather than trusting the header value outright.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a `customers/data_request` webhook, capturing the exact raw body `B` and the `x-shopify-hmac-sha256` value `H` that Shopify sent for that delivery.
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unmodified)
   - Header `x-shopify-hmac-sha256`: `H` (unmodified)
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic`: `customers/data_request` (unmodified)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and finds it matches `H`, since the header substitution is never part of the signed string: [4](#0-3) 
4. The registered handler is invoked with `WebhookMetadata.new(topic: "customers/data_request", shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the application to process/act as if `victim-shop` sent this webhook, despite the payload actually originating from the attacker's own shop.

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
