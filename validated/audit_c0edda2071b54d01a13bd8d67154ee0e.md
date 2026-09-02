Confirmed: `ShopifyAPI::Webhooks::Request#hmac` is computed only over `to_signable_string`, which returns `@raw_body` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` fields are all read directly from unauthenticated HTTP headers and are never part of the signed content [2](#0-1) . `HmacValidator.validate` only checks `verifiable_query.hmac` against `HMAC(secret, to_signable_string)`, i.e., the body [3](#0-2) . `Registry.process` passes the header-derived `request.shop` and `request.topic` straight into `WebhookMetadata` given to the host app's handler once only the body HMAC has passed [4](#0-3) .

### Title
Webhook `shop`/`topic` attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw JSON body via HMAC, while the `shop-domain`, `topic`, `api-version`, and `webhook-id` values used to route and attribute the webhook are taken from unauthenticated HTTP headers. Because a single app's `client_secret` (the HMAC key) is shared across every merchant shop that installs the app, any merchant who receives a legitimately signed webhook for their own shop can replay that exact body with a forged `shopify-shop-domain` (and/or `shopify-topic`) header pointed at a victim shop. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will hand the attacker-chosen `shop`/`topic` to the host application's handler as if Shopify itself attested to them.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, shop || topic || body)` (or equivalent, binding tenant identity to the signature). Instead the gem enforces only:

`hmac == HMAC(secret, body)`

with `shop` and `topic` supplied separately and unauthenticated:
- `to_signable_string` returns solely `@raw_body` [1](#0-0) .
- `shop`, `topic`, `api_version`, `webhook_id` are pulled from HTTP headers with no cryptographic tie to the HMAC [2](#0-1) .
- `HmacValidator.validate`/`validate_signature` compute and compare the digest solely over `verifiable_query.to_signable_string` [5](#0-4) .
- `Registry.process` trusts `request.shop` and `request.topic` once body-HMAC validation succeeds, and forwards them unchanged to the app-supplied handler via `WebhookMetadata` [4](#0-3) .

Since the API secret (`client_secret`) is per-app, not per-shop, any of the app's own installed merchants can capture one of their own legitimately-delivered webhook payload+HMAC pairs (e.g., by installing the app, which is unprivileged from the app's perspective — it's the normal, expected way to interact with a Shopify app), and replay the identical body with the `shopify-shop-domain`/`shopify-topic` headers rewritten to name a different, victim shop. `HmacValidator.validate` will report success because the body bytes and HMAC still match, and `Registry.process` will invoke the handler believing the event genuinely originated from — and concerns — the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the gem is trusted to enforce for webhook delivery, matching the "cross-tenant access" Critical impact category. Any host application that uses `WebhookMetadata#shop` to decide which merchant's records to update, or `WebhookMetadata#topic` to decide what action to take (e.g. `app/uninstalled`, `shop/redact`, order or customer data writes), can be made to attribute another shop's data mutation, deletion, or webhook-triggered side effects to a spoofed tenant — entirely from the perspective of `shopify_api`'s own verification logic, since the gem asserts the request is authentic ("Invalid webhook HMAC" is never raised) despite the tenant-identifying fields being forged.

### Likelihood Explanation
Exploitation requires only that the attacker be one of the app's own installed merchants (an ordinary, unprivileged interaction with a public app — no `api_secret_key`, access token, or credential theft needed) and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is inherent to how webhook delivery works (the endpoint must accept unauthenticated inbound POSTs). No race condition or timing dependency is needed; the attacker simply needs one previously-received, validly-signed webhook body for their own shop to replay with a different `shop-domain`/`topic` header.

### Recommendation
Bind the tenant/topic identity into the signed material verified by `HmacValidator`, e.g. have `Request#to_signable_string` incorporate `shop`, `topic`, and `webhook_id` alongside the raw body (matching what Shopify computes when signing, if supported), or otherwise cryptographically verify that the headers correspond to the shop/topic Shopify actually sent by cross-checking against a known/expected value (e.g. requiring the app to confirm the reporting shop has an active session/installation record before trusting `data.shop`, and documenting this requirement clearly since `shopify_api` itself cannot enforce it without header inclusion in the signature).

### Proof of Concept
1. Malicious actor `M` installs the target app on `shop-m.myshopify.com` (a normal user action, no privilege required).
2. Shopify delivers a legitimate webhook to the app's endpoint for `shop-m`, e.g. `orders/create`, with body `B` and header `shopify-hmac-sha256: H` where `H = Base64(HMAC-SHA256(client_secret, B))`. `M` captures `B` and `H` (they control their own server logs/network capture for their own shop's webhook).
3. `M` sends a new POST to the app's public webhook endpoint reusing body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`, e.g. `app/uninstalled`, if the topic-specific body format doesn't matter to the target handler).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and finds it equal to `H` — validation succeeds because the shop/topic headers are never part of the signed input [6](#0-5) [7](#0-6) .
5. The registered handler receives `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", body: ..., ...)` and performs whatever tenant-scoped action the host app implements (e.g., deleting local records for `victim-shop`), even though Shopify never sent any event about `victim-shop` [8](#0-7) .

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
