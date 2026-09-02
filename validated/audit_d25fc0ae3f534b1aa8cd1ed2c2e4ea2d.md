### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are read from unauthenticated HTTP headers while the HMAC only signs the raw body, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `api_version`, and `webhook_id` values from HTTP headers, but its `to_signable_string` (used by `Utils::HmacValidator`) only signs the raw request body. This breaks the intended binding: *the shop that the HMAC-verified body was generated for* must equal *the shop the app attributes the webhook to*. Because the header carrying the shop identity is not covered by the signature, an attacker who possesses one validly-signed webhook body/HMAC pair can relabel it for a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, `#webhook_id` are all read straight from HTTP headers, none of which participate in the signable string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` against `verifiable_query.hmac`, i.e. it verifies the body bytes only: [3](#0-2) 

`Registry.process` validates the HMAC and then hands `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` straight to the app-supplied handler as `WebhookMetadata`, treating them as trusted, verified identity fields: [4](#0-3) 

The equality the HMAC is supposed to guarantee is: `hmac == HMAC(secret, body_bytes_for_shop_X)` implies `shop == X`. In reality the check only proves `hmac == HMAC(secret, body_bytes)`; `shop` (and `topic`/`webhook_id`/`api_version`) is an independent, attacker-controlled header value with no cryptographic tie to the body. Before the attack: attacker installs the app on their own shop A (an ordinary, unprivileged action) and receives a legitimately-signed webhook `(body_A, hmac_A, shop-domain: A)`. After the attack: attacker resends `(body_A, hmac_A, shop-domain: B)` to the app's webhook endpoint. `HmacValidator.validate` still returns `true` (body/HMAC pair unchanged), so `Registry.process` dispatches `WebhookMetadata.new(shop: "B", body: body_A, ...)` to the app's handler, i.e. shop A's payload is delivered and processed as if it belongs to shop B.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` to decide which merchant's session/records to act on (a normal and expected usage pattern for this field, since it is the only shop identifier exposed on the callback) will apply shop A's webhook body to shop B's tenant context. This is a cross-tenant data-confusion primitive delivered entirely through the gem's own verification logic (`HmacValidator` + `Webhooks::Request` + `Webhooks::Registry.process`), not a documented API misuse by the host app — the gem itself asserts these header-derived values are meaningful post-HMAC-validation fields (they are passed straight into the verified callback).

### Likelihood Explanation
The attacker only needs to be an ordinary merchant/installer of the target app (no `api_secret_key`, access token, or privileged role required) to obtain one genuine `(body, hmac)` pair, then replay it toward the app's public webhook endpoint with a modified `shop-domain` header. No TLS interception or secret leakage is needed since the header is never protected by the signature in the first place.

### Recommendation
Include the shop-identifying header (and topic/webhook-id/api-version, or at minimum `shop-domain`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the header values to the body before trusting `request.shop` in `Registry.process`/`WebhookMetadata`. Alternatively, require host applications to independently confirm that `webhook_id`/`shop` corresponds to a webhook subscription actually registered for that shop before acting on the payload.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and lets the app register a webhook subscription.
2. Shopify delivers a legitimately-signed webhook to the app's endpoint: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request (e.g., via their own reverse proxy/logging in front of the app, which they control since it's their own installation) and resends it to the same endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the tampered headers; `Utils::HmacValidator.validate` recomputes the HMAC over the unchanged body `B` and it matches, so validation succeeds [5](#0-4) .
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` and forwards it to the app's handler [6](#0-5) , causing the app to process attacker-controlled/attacker-shop data under the victim shop's identity.

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
