Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes the HMAC solely over that signable string [2](#0-1) , so `shop`, `topic`, `api_version`, and `webhook_id` (all parsed from unauthenticated HTTP headers) are never bound into the signature. `Registry.process` trusts `request.shop` straight from that unverified header when constructing the `WebhookMetadata` handed to the app's handler [3](#0-2) .

### Title
Webhook tenant identity (`shop`) is not bound by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator` verifies the HMAC exclusively against that body string. The `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are read directly from attacker-influenceable HTTP headers and are never part of the signed payload, yet `Webhooks::Registry.process` passes `request.shop` unchecked to the app's `WebhookHandler` as the tenant identifier.

### Finding Description
This mirrors the H-2 bug class: a value that drives a privileged/tenant-scoped action (`_rewardProportion` in the Sherlock report) is not covered by the validation that is supposed to bind it (input-range check in that case; HMAC signature here). In this gem:

- `Request#hmac` decodes the `hmac-sha256` header, and `Request#to_signable_string` returns `@raw_body` only [4](#0-3) .
- `HmacValidator.validate` recomputes `HMAC(secret, to_signable_string)` and compares it to the received value with `OpenSSL.secure_compare` [2](#0-1) .
- Because the signature only covers `@raw_body`, any request carrying a `raw_body` + `hmac-sha256` pair that is valid for the configured `api_secret_key` will pass validation *regardless of the `shop-domain` header value*.
- `Registry.process` then builds `WebhookMetadata` using `request.shop` — taken straight from the unauthenticated `shop-domain`/`x-shopify-shop-domain` header — and hands it to the host app's handler as the trusted tenant identity [3](#0-2) .

Equality that should hold but doesn't: `shop header authenticated` == `shop header covered by HMAC`. In reality: `HMAC covers {raw_body}` while `tenant identity used downstream = shop-domain header` (uncovered).

A merchant who has installed the app on their own store legitimately receives real webhooks with a valid `(raw_body, hmac)` pair for their own shop. Because the `shop-domain` header isn't part of the signed material, that same merchant can replay the identical `raw_body`/`hmac` pair while substituting an arbitrary `shop-domain` header (e.g. a victim shop they don't own). `Utils::HmacValidator.validate` still succeeds because it only re-derives the signature from the body, and `Registry.process` forwards the attacker-chosen `shop` value to the app's webhook handler as if it were authenticated.

### Impact Explanation
This breaks the tenant boundary the webhook system is meant to enforce: an app's `WebhookHandler.handle` implementation receives `data.shop` believing it to be a value Shopify has vouched for, when in fact it is fully attacker-controlled. Any host application that uses `data.shop` to look up per-tenant state, credentials, or authorization decisions (which is the documented intended use per `docs/usage/webhooks.md` and `BREAKING_CHANGES_FOR_V15.md`, both instructing apps to key work off `data.shop`) can be tricked into processing attacker-supplied data under another merchant's identity — a cross-tenant access condition.

### Likelihood Explanation
Exploitation requires no privileged credentials or knowledge of `api_secret_key`: any entity that can install the app on any shop (a completely ordinary, low-privilege action available to any Shopify merchant) can capture one legitimate webhook delivery (body + valid signature) and replay it with a forged `shop-domain` header to the app's public webhook endpoint. This is a realistic, low-effort attack path.

### Recommendation
Include `shop-domain` (and ideally `topic`/`api-version`/`webhook-id`) in the HMAC-covered signable string, or independently verify that the `shop-domain` header corresponds to a shop the app has an active installation/session for before trusting `request.shop` in `Registry.process`. At minimum, document that host applications must not treat `data.shop` as authenticated and must cross-check it against a known/installed shop list.

### Proof of Concept
1. App merchant installs the target app on `attacker-shop.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`, plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. The merchant (attacker) captures `B` and `H`, then sends a new request to the same webhook endpoint reusing body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, B) == H` [5](#0-4) .
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is constructed with `shop == "victim-shop.myshopify.com"` and passed to the app's `handle` method, causing the app to process attacker-supplied body content as if it came from the victim shop [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
