This confirms the vulnerability. The `ShopifyAPI::Webhooks::Request` HMAC signature only covers `@raw_body` (via `to_signable_string` returning `@raw_body` at `lib/shopify_api/webhooks/request.rb:36-38`), while the `shop`, `topic`, `api_version`, and `webhook_id` fields are all read directly from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:16-33`) that are never included in the signed payload.

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)` at `lib/shopify_api/webhooks/registry.rb:190`, then trusts `request.shop` and `request.topic` to select the handler and populate `WebhookMetadata` at `lib/shopify_api/webhooks/registry.rb:192-199`. Since the app's `client_secret`/`api_secret_key` is shared across all shops using the app (not shop-specific), any attacker who can trigger a legitimate webhook to their own shop's endpoint (e.g., by installing the app on a store they control and firing an event with attacker-influenced body content) obtains a `(raw_body, hmac)` pair that is valid regardless of which `shop-domain`/`topic`/`webhook-id` headers accompany it. The attacker can then replay that exact body+hmac to the app's webhook endpoint while forging the `shop-domain` header to point at a victim shop, and `HmacValidator.validate` at `lib/shopify_api/utils/hmac_validator.rb:26-31` will still pass because it only checks `to_signable_string` (the body) against the secret — it never binds the signature to the shop asserted in the header.

### Title
Webhook HMAC does not bind the `shop-domain`/`topic` headers, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers from the HMAC computation. `Registry.process` trusts these unauthenticated headers to determine which shop and topic a webhook belongs to, after validating only the body's HMAC.

### Finding Description
The identity binding broken here is: `HMAC-verified content == body` but `tenant identity used by handler == request.shop` (an unauthenticated header). These are not the same set of bytes.

In `lib/shopify_api/webhooks/request.rb`:
- `shop` (line 20-23), `topic` (line 15-18), `webhook_id` (line 30-33), and `api_version` (line 25-28) are all sourced from `shopify_header`, i.e., raw HTTP headers supplied by whoever POSTs to the app's webhook endpoint.
- `to_signable_string` (line 35-38) returns only `@raw_body`.

In `lib/shopify_api/webhooks/registry.rb:189-199` (`process`), the only authentication check performed is:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
which (per `lib/shopify_api/utils/hmac_validator.rb:26-31`) computes `HMAC(api_secret_key, raw_body)` and compares it to the `hmac-sha256` header — nothing more. After this single check passes, `request.shop`, `request.topic`, and `request.webhook_id`/`api_version` (all unauthenticated) are handed to the registered handler via `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`.

Because the `api_secret_key` is a single per-app secret (not per-shop), any valid `(raw_body, hmac)` pair produced by Shopify for *any* shop that has the app installed — including a shop the attacker controls — remains a cryptographically valid pair for that same body regardless of which shop or topic header accompanies it. An attacker who installs the app on their own store can trigger events (e.g., product/order webhooks whose body content they can partially control) to capture a legitimate `(raw_body, hmac)` pair, then POST that identical body and HMAC to the victim app's public webhook endpoint while substituting the `shop-domain` header for a different (victim) shop's domain. `Utils::HmacValidator.validate` will still return `true`, and the handler will process the payload believing it originates from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: a webhook payload can be attributed to an arbitrary shop chosen by the attacker via an unauthenticated header, even though only the body bytes are cryptographically verified. Any host application that uses `WebhookMetadata#shop` to key data writes, trigger side effects, or make authorization decisions per-tenant can be made to apply attacker-influenced webhook content to a shop the attacker does not own — a cross-tenant access/data-integrity violation, which the rules classify as Critical.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even trial) merchant able to install the app on a shop they control and trigger at least one webhook delivery with body content useful to them, plus the ability to send an arbitrary HTTP request with custom headers to the app's public webhook endpoint (which is by definition internet-reachable). No access token, `client_secret`, or privileged account is needed. This is squarely an unprivileged-internet-user path, matching the "field acted on but not covered by the HMAC" analog class.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material used for HMAC validation, or otherwise cryptographically bind the shop/topic to the verified payload (e.g., verify the shop against a value embedded in the HMAC-signed body, or require a per-shop secret/nonce). At minimum, `Registry.process` should not trust `request.shop`/`request.topic` for tenant-identification purposes unless those fields are covered by the same signature that authenticates the body.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `products/update`) with body content the attacker can influence.
2. Shopify computes and sends `X-Shopify-Hmac-SHA256: H` where `H = HMAC-SHA256(api_secret_key, raw_body)`, along with `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `(raw_body, H)`.
4. Attacker sends a POST directly to the app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-SHA256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally a different `X-Shopify-Topic`).
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against `H` (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
6. The registered handler for the topic executes with `WebhookMetadata#shop == "victim.myshopify.com"` and attacker-influenced `body`, despite the request never having been authenticated for that shop. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
