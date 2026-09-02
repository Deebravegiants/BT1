### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used for dispatching webhook data from the `shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator.validate` is computed only over the raw request body (`to_signable_string` returns `@raw_body`). The `shop-domain` header is never included in the signed bytes, so the "shop" identity bound to a webhook payload has no cryptographic link to the signature that authenticates it.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` is defined as the raw body only: [3](#0-2) 

Meanwhile `shop` is read straight from an unsigned header: [4](#0-3) 

After HMAC validation passes, `process` uses this unauthenticated `request.shop` value to build the `WebhookMetadata` passed to the app's handler: [1](#0-0) 

This breaks the intended binding: `shop_that_HMAC_authenticates == shop_the_handler_acts_on`. In reality, the HMAC only authenticates `(client_secret, raw_body)`; the `shop` field that flows into `WebhookMetadata#shop` (documented as "The shop domain of the webhook", per `docs/usage/webhooks.md`) is fully attacker-controlled at the header level and can be set to any value while a *different*, unrelated valid `(body, hmac)` pair is attached.

Because the app's `client_secret` is shared across *all* installations of the app (it is not shop-specific), any actor who can get the app installed on their own store — an "unprivileged internet user" with respect to any *other* merchant's tenant — can trivially obtain a body/HMAC pair that passes `HmacValidator.validate` (e.g., by triggering a real webhook delivery to their own shop, or, depending on the app's webhook body content, by computing it themselves if the body is attacker-influenced). They can then submit that legitimately-signed body to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` / `shopify-shop-domain` header naming a victim shop. `ShopifyAPI::Webhooks::Registry.process` will accept it (the HMAC over the body checks out) and hand the handler a `WebhookMetadata` claiming the data originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who legitimately installs the app on one (their own) shop can forge webhook events that the host application will process as if they came from a victim shop of the attacker's choosing, since `WebhookMetadata#shop` — the only tenant identifier passed to application handlers — is never covered by the signature that "authenticates" the webhook. Downstream, any host application that uses `data.shop` to select which merchant's records to update, queue jobs against, or drive business logic (exactly as shown in the gem's own documented example: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be made to attribute attacker-supplied webhook content to another tenant. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Medium-to-High. Exploitation requires only:
1. The ability to install the target app on any shop (including one controlled by the attacker) to obtain at least one legitimately HMAC-signed `(body, hmac)` pair — no leaked secrets or privileged access needed.
2. Direct HTTP access to the app's public webhook endpoint (which by design is internet-reachable, as it must accept unauthenticated POSTs from Shopify's infrastructure).
3. Free control over HTTP headers when submitting the forged request, since headers are never included in the signed content.

No `api_secret_key`, access token, or other credential of the victim is required — only participation as an ordinary, unprivileged merchant/attacker of the app.

### Recommendation
- Do not derive the tenant-identifying `shop` value used by `WebhookMetadata` solely from an unsigned header. Require the raw body (or an explicitly-signed field) to carry the shop identity and cross-check it against the header, rejecting mismatches.
- Where possible, bind webhook processing to registrations recorded per-shop (e.g., verify that the shop named in the request has an active webhook registration/session before dispatching), so a mismatched or unexpected shop cannot be delivered to a handler.
- Document prominently in `docs/usage/webhooks.md` that `data.shop` is not part of the HMAC-covered bytes and must not be trusted as an authenticated tenant identifier without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, obtaining a legitimately signed webhook delivery (or otherwise obtains any valid `(raw_body, hmac)` pair verifiable with the app's shared `client_secret`).
2. Attacker sends a direct HTTP POST to the app's public webhook endpoint with:
   - Body: the captured valid `raw_body`
   - Header `shopify-hmac-sha256`: the captured valid HMAC for that body
   - Header `shopify-shop-domain`: `victim-shop.myshopify.com` (arbitrary, attacker-chosen)
   - Header `shopify-topic`: the original topic
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this into a `Request` whose `shop` returns `"victim-shop.myshopify.com"`. [5](#0-4) 
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC is computed only over `raw_body`, unaffected by the header change. [1](#0-0) 
5. The registered handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` and performs its documented action (e.g., `perform_later(shop_domain: data.shop, ...)`) under the impersonated victim shop identity — despite the attacker never having any credential or session tied to that victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```
