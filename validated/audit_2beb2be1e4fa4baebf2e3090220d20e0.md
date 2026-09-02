### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies its HMAC over the raw request body only, while the `shop`, `topic`, and `webhook_id` values that are passed to the app's webhook handler are read directly from unauthenticated HTTP headers. This breaks the identity binding `HMAC(secret, X) == received_hmac` should imply `X` (including the claimed shop) is authentic — here `X` is only the body, not the shop/topic/webhook_id.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over whatever `to_signable_string` returns and compares it to the `hmac-sha256` header value: [2](#0-1) 

`Registry.process` accepts the request purely based on that body-only HMAC check, then builds `WebhookMetadata` directly from the `shop`, `topic`, and `webhook_id` accessors, which read raw headers with no cryptographic binding: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `HMAC_valid(body) ⇒ shop_header == actual_originating_shop`. Instead, the code only proves `HMAC_valid(body)`; `shop`, `topic`, and `webhook_id` are parsed from the request but never verified as part of the signed material — analogous to the report's root cause where a value that participates in downstream logic (`oldShares`) is not properly accounted for in the calculation that is supposed to validate it (`_totalSupply`).

### Impact Explanation
Any actor able to submit a syntactically valid webhook body signed with the app's own `client_secret` — most plausibly a genuine merchant who has that app installed on their own store and thus legitimately receives real, correctly-HMAC'd webhooks for their own shop — can capture one such request and replay it to the app's webhook endpoint with the `shopify-shop-domain`, `shopify-topic`, and/or `shopify-webhook-id` headers rewritten to arbitrary values. Because those headers are not part of the signed payload, `Utils::HmacValidator.validate` still returns `true`, and `WebhookMetadata#shop`/`#topic` will contain attacker-chosen values that the host application's `WebhookHandler#handle` implementation is documented to trust for tenant/session lookup and topic dispatch. This enables cross-tenant data injection or spoofing of a webhook as belonging to a different merchant's shop or a different topic than actually occurred, which falls under Critical - cross-tenant access.

### Likelihood Explanation
Reaching this requires only a body+HMAC pair that is genuinely valid for the target app's secret — trivially obtainable by any merchant/user who has the app installed on any shop (a normal, unprivileged relationship with the app, not requiring the app's `client_secret`, an access token, or any privileged position). No TLS interception, credential theft, or social engineering is needed; only forging/replaying HTTP headers on a request the attacker already legitimately received. This is a concrete, directly reachable gap in this gem's own verification code (`Request`/`HmacValidator`), not a defect requiring the host app to violate documented usage.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (in addition to the body) in the signable string used for HMAC verification, or otherwise cryptographically bind them (e.g., derive/verify them from data embedded in the signed body, or require the host to re-validate `shop` against its own session store before trusting `WebhookMetadata#shop`). At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id` are unauthenticated header values not covered by HMAC verification, so integrators do not use them for tenant routing without additional validation.

### Proof of Concept
1. App has the tested gem installed and receives a legitimate webhook from Shopify for `victim-shop.myshopify.com`, topic `orders/create`, with headers `shopify-hmac-sha256: <valid-hmac-of-body>`, `shopify-shop-domain: attacker-or-victim-shop...`, `shopify-topic: orders/create`, and some `webhook_id`.
2. Attacker (who legitimately has the app installed on their own shop, `attacker-shop.myshopify.com`) intercepts/logs one of their own genuinely-signed webhook requests (body + `hmac-sha256`).
3. Attacker resends the exact same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com` and/or a different `shopify-topic`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the body against the HMAC — [5](#0-4)  — and `Registry.process` proceeds to invoke the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: <attacker-chosen>, ...)` — [3](#0-2) .
5. Any host application logic that keys tenant/session lookups or business actions off `data.shop`/`data.topic` from `WebhookMetadata` will act as if the event genuinely originated from `victim-shop.myshopify.com` under the spoofed topic.

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
