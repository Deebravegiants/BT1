### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then dispatches the event to the app's handler using a `shop` value that is read from an HTTP header and is **not** part of the signed material. The binding the code implicitly assumes — "the shop that receives credit for this event equals the shop the HMAC was computed for" — does not actually hold, because the HMAC only covers `@raw_body`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body was signed by Shopify with the app's `api_secret_key`), and — once that check passes — trusts the unauthenticated `request.shop` header to build the `WebhookMetadata` that is handed to the app's handler as the tenant identity for the event: [3](#0-2) 

`HmacValidator.validate` computes/compares the signature only over `verifiable_query.to_signable_string`, which for webhooks is the body only: [4](#0-3) 

The equality the code needs but never checks is: `hmac == HMAC(secret, body)` AND `shop == "the shop this specific delivery was generated for"`. Because the header is unsigned, an attacker who can obtain (or replay) any single genuine `(raw_body, hmac)` pair produced for the app's shared `api_secret_key` can resubmit it with an arbitrary `shop-domain` header, and `Registry.process` will accept it and attribute the payload/event to that other, attacker-chosen shop — a cross-tenant confusion inside this gem's own verification logic. This mirrors the report's root cause: a field the code *acts on* (the tenant/shop identity used for dispatch) is not covered by the same authenticator (HMAC) used to accept the request, unlike the OAuth `AuthQuery`, where `shop` is explicitly included in `to_signable_string` and thus is bound to the HMAC: [5](#0-4) .

### Impact Explanation
If successfully triggered, this results in cross-tenant data confusion at the webhook-processing layer: a webhook body legitimately generated for shop A can be delivered to the app's handler labeled as belonging to shop B, causing the app to update, create, or act on shop B's tenant record using shop A's data (or vice versa). This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to possess a valid `(raw_body, hmac)` pair, which can only be produced by Shopify itself using the app's `api_secret_key` (unknown to any external/unprivileged party) — the attacker cannot forge an arbitrary body themselves. A concrete unprivileged path to *obtain* such a pair for replay against a chosen victim shop, without network interception of Shopify's genuine delivery, was not identified in this gem's code. This weakens the practical likelihood considerably, and the strongest available path effectively depends on the ability to capture a legitimate delivery, which borders on the excluded "TLS interception" precondition. I cannot confirm a self-contained, unprivileged exploitation path within this gem alone; the root-cause defect (unsigned shop identity) is real and clearly demonstrated in the cited code, but end-to-end exploitability without network-level assistance is uncertain.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) identity into the value that is authenticated, e.g. by requiring callers to additionally pass an expected shop (from session/tenant routing) and comparing it against `request.shop` only after confirming that combination via a signed channel, or by having `Registry.process` require the caller to supply the shop it expects and reject mismatches, rather than trusting the header value implicitly for tenant attribution once the body-only HMAC passes.

### Proof of Concept
Not fully constructible with unprivileged-internet-user primitives alone: forging a valid `(raw_body, hmac)` pair requires the app's `api_secret_key`, which is not obtainable through this gem's code paths without violating the exclusions (credential leakage, TLS interception). This limits the finding to a demonstrated root-cause code defect (unsigned tenant-identity header) rather than a fully verified exploit chain: [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** test/webhooks/registry_test.rb (L304-314)
```ruby
      def test_process_hmac_validation_fails
        headers = {
          "x-shopify-topic" => "some/topic",
          "x-shopify-hmac-sha256" => "invalid",
          "x-shopify-shop-domain" => "shop.myshopify.com",
        }

        assert_raises(ShopifyAPI::Errors::InvalidWebhookError) do
          ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: headers))
        end
      end
```
