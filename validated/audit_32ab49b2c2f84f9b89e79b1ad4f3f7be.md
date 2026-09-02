Confirmed: the `ShopifyAPI::Webhooks::Registry.process` flow validates only the HMAC of the raw body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` header values verbatim to build `WebhookMetadata` and dispatch to the app's handler — these header fields are never covered by the HMAC signature.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the body, not the routing headers - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , and `Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over that signable string [2](#0-1) . `Registry.process` uses this single check as the sole authenticity gate, then trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all read straight from unauthenticated HTTP headers — to build the `WebhookMetadata` passed to the app's handler [3](#0-2) . Those header accessors simply pull values out of the headers hash with no cryptographic binding [4](#0-3) .

### Finding Description
The identity binding that should hold is: `hmac_valid(body) == (shop, topic recorded in the same signed message)`. In this gem, the equality instead reduces to `hmac_valid(body)` while `shop`/`topic`/`webhook_id`/`api_version` are taken from headers that are outside the signed material. The webhook HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has the app installed — it is not shop-specific. Consequently, any tenant with the app installed legitimately receives real `(raw_body, hmac)` pairs signed with that shared secret. Because the HMAC never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers, an attacker who controls one installed shop can capture a genuine `(raw_body, hmac)` pair from their own webhook deliveries and replay that exact body+HMAC to the app's webhook endpoint while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a different tenant. `Utils::HmacValidator.validate` will report the request as valid — the signature over the body is correct — and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop/topic, even though that shop never sent this data [5](#0-4) .

### Impact Explanation
This is a cross-tenant identity confusion: application logic keyed on `data.shop` (e.g. attributing orders, triggering per-shop side effects, looking up/deleting shop-scoped records, or acting on mandatory topics like `shop/redact` or `app/uninstalled`) can be triggered under an attacker-chosen shop identity using data/authenticity borrowed from a different, attacker-controlled tenant. Because host apps are explicitly documented to key their processing off `data.shop` and `data.topic` [6](#0-5) , this can let a malicious merchant with the app installed cause the app to process fabricated webhook events attributed to another shop it does not control — a cross-tenant boundary break rooted directly in this gem's verification code, not merely host misuse.

### Likelihood Explanation
Exploitation only requires the attacker to install the target app on any shop they control (a normal, unprivileged action for any Shopify merchant/developer) and to be able to send arbitrary HTTP requests to the app's public webhook endpoint with attacker-chosen headers — no access token, `client_secret`, or privileged account is needed. The HMAC check passes unmodified because it validates body bytes only, not the header-derived identity fields that the handler actually acts on.

### Recommendation
Bind the routing/identity headers into the signed material verified by `HmacValidator`, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the verified body (e.g., include them in `to_signable_string`, or require the app to independently verify that the `shop` header corresponds to a shop with an active session for the webhook's registered topic before dispatch). At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated header values and must not be trusted for tenant-authorization decisions without an additional check against a known/installed-shop list.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; the app registers, e.g., the `orders/create` webhook.
2. Trigger a real order event on `attacker.myshopify.com` so Shopify sends a legitimately-signed webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Capture `(B, HMAC(secret, B))` from that request (attacker fully controls their own inbound traffic/logs).
4. Replay a request directly to the app's webhook endpoint with the same `raw_body = B` and the same `x-shopify-hmac-sha256` value, but with `x-shopify-shop-domain: victim-shop.myshopify.com` substituted.
5. `Utils::HmacValidator.validate` returns `true` (body signature matches) [7](#0-6) ; `Registry.process` dispatches `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` to the app's handler [8](#0-7) , causing the app to process attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-21)
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

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
