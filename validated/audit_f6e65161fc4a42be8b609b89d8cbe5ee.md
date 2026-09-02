### Title
Webhook shop identity (`shop-domain` header) is not covered by the HMAC signature, allowing shop-attribution spoofing/replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), `topic`, `api_version`, and `webhook_id` entirely from HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. `Registry.process` validates the HMAC and then trusts `request.shop` to attribute the webhook payload to a specific merchant, without that value ever being part of the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read from unauthenticated headers (`X-Shopify-Shop-Domain`, etc.) that are never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the HMAC against `to_signable_string` (i.e., the body only) and, once that check passes, unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever sees `to_signable_string`, so it cannot detect if the `shop-domain` header has been altered: [4](#0-3) 

The identity binding that should hold is: `hmac == HMAC(client_secret, shop ‖ topic ‖ body)` such that the shop the app acts on is cryptographically bound to the signature. Instead, the actual binding implemented is `hmac == HMAC(client_secret, body)` with `shop` supplied out-of-band via a header. Because a valid `(body, hmac)` pair is reusable with any header set, a merchant who receives legitimate webhooks for their own store (which they can trigger themselves, e.g. by creating/updating resources) obtains a genuine, correctly-signed `(raw_body, hmac)` pair. They can then replay that exact body/HMAC directly against the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (same body, same secret), but `WebhookMetadata#shop` now reports the victim shop. Any handler that keys persistence, deletion, or business logic off `data.shop` (as intended by the `WebhookMetadata` contract) will act as if the event happened on the victim's store.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: an attacker with no access to the app's `client_secret`, access tokens, or the victim's credentials can cause the app to process attacker-supplied webhook bodies under a victim shop's identity. Depending on the topic (e.g., mandatory `shop/redact`, `customers/redact`, `customers/data_request`, or an app-registered order/product webhook), this can cause cross-tenant data corruption, spurious redaction/deletion for another merchant, or state confusion tied to the wrong tenant — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to operate their own Shopify store with the vulnerable app installed (to obtain valid `(body, hmac)` pairs for topics they control) and to be able to send arbitrary raw HTTP requests directly to the app's public webhook endpoint (bypassing Shopify's delivery). No secret material, TLS interception, or social engineering is needed — only observation of legitimate webhook traffic to their own store and header manipulation on replay, both of which are within reach of an "unprivileged internet user" who is a merchant of their own shop.

### Recommendation
Bind the tenant/topic identity into the signed material, or otherwise cross-check it against a source that is authenticated. Concretely:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (mirroring how `AuthQuery#to_signable_string` binds `shop`, `state`, `host`, etc. into its HMAC input), or
- Independently verify `request.shop` against session/shop data known to the app (e.g., only accept webhooks for shops with an active, previously-established `offline_<shop>` session) before trusting `WebhookMetadata#shop` in `Registry.process`, and
- Document/enforce that consumers must not rely on `request.shop` without this additional binding.

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Attacker triggers the webhook by creating an order in their own store; Shopify delivers a POST to the app's webhook endpoint with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac over raw body>`, and a JSON body.
3. Attacker captures this exact `(raw_body, hmac)` pair (they control the traffic to their own endpoint/proxy).
4. Attacker crafts a new HTTP POST directly to the app's public webhook endpoint, reusing the identical `raw_body` and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds (since body/secret/hmac are unchanged) — see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`.
6. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though the payload was never signed for that shop — see `lib/shopify_api/webhooks/registry.rb:188-200`.

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
