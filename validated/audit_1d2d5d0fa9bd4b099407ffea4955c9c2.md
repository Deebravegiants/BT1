Confirmed: `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) only validates `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`). The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled from HTTP headers (`lib/shopify_api/webhooks/request.rb:15-33`) that are never included in the HMAC-signed payload, yet they are trusted downstream and handed to the app's handler as `WebhookMetadata` (`lib/shopify_api/webhooks/registry.rb:198-199`).

### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` fields, which are read from HTTP headers and passed to the app's webhook handler as trusted routing/attribution metadata, are never included in the HMAC-signed content.

### Finding Description
`Registry.process(request)` calls `Utils::HmacValidator.validate(request)` [1](#0-0) , which computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it against the HMAC header using `OpenSSL.secure_compare` [2](#0-1) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [3](#0-2) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors, however, are all read directly from HTTP headers [4](#0-3) , none of which is part of the signed content.

After validation succeeds, `process` looks up a handler purely by `request.topic` and invokes it with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id)` [5](#0-4) . The equality the gem is implicitly claiming to enforce is: *"the shop/topic attributed to this webhook body equals the shop/topic Shopify actually sent this body for."* Because the header fields are outside the HMAC's scope, that equality is never checked — only "the body bytes are unmodified from some HMAC-valid webhook" is checked, not "these specific headers belong to this body."

This is exploitable by an unprivileged internet user who legitimately owns any Shopify store (e.g., a free development store) capable of receiving real webhooks for that shop:
1. The attacker registers a webhook (or receives any mandatory webhook, e.g. `customers/data_request`) on their own store and captures a genuine `(raw_body, hmac-sha256)` pair Shopify sent them — this pair is valid and signed with the target app's real `client_secret` because Shopify computed it, not the attacker.
2. The attacker replays this exact `raw_body` to the victim app's webhook endpoint, but substitutes the `X-Shopify-Shop-Domain` header with a different, victim shop's domain, and/or substitutes the `X-Shopify-Topic` header to route it to a different handler.
3. `HmacValidator.validate` still succeeds, because the HMAC only ever attested to `raw_body`, which is byte-for-byte identical to what was captured.
4. `Registry.process` dispatches the (attacker-supplied) `shop` and `topic` to the app's handler as if Shopify itself vouched for that shop/topic pairing.

### Impact Explanation
This breaks the binding between the request body content and the shop/topic it is attributed to, letting an unprivileged internet user cause the app's webhook handler to process attacker-controlled body content while it is misattributed to an arbitrary victim shop domain (which the attacker does not own) or misrouted to an arbitrary registered topic handler. Any state (e.g., mandatory GDPR redact/data-request handling, inventory/order processing side effects) that the host application keys off `WebhookMetadata#shop` or `#topic` can be corrupted or triggered for a tenant the attacker doesn't control — a cross-tenant data-attribution bypass rooted entirely in this gem's `Webhooks::Request`/`Registry` implementation.

### Likelihood Explanation
Likelihood is moderate-to-high for any attacker who can register/operate a Shopify development store (free, unprivileged) and simply capture a legitimate webhook delivery aimed at their own shop, then replay it with modified headers to the same app's public webhook endpoint. No access token, `client_secret`, or privileged credential is required — only a real webhook payload the attacker was legitimately sent, which is the only artifact needed to pass the gem's HMAC check.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the HMAC-signed content that `Webhooks::Request#to_signable_string` returns, or otherwise cryptographically bind them to the raw body before trusting them in `Registry.process`. At minimum, the host application should be required (and the gem should facilitate) verifying that `request.shop` matches an expected/known shop for the session under which the webhook was registered before acting on `WebhookMetadata`.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and receives a real webhook from Shopify:
captured_body = '{"id":123,"note":"hello"}'
captured_hmac_header = "<base64 hmac Shopify computed with the app's real client_secret>"

# Attacker replays the identical body/hmac to the victim app's endpoint,
# but swaps the shop-domain and topic headers:
forged_headers = {
  "x-shopify-topic" => "customers/data_request",       # attacker-chosen topic
  "x-shopify-hmac-sha256" => captured_hmac_header,       # unchanged, still valid for captured_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # NOT the attacker's shop
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (lib/shopify_api/utils/hmac_validator.rb only checks captured_body),
#    and the handler receives WebhookMetadata with shop: "victim-shop.myshopify.com",
#    topic: "customers/data_request" though Shopify never sent this body for that shop/topic.
```

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
