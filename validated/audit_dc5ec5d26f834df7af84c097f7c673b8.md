Confirmed: the webhook HMAC signs only `@raw_body` (`to_signable_string` returns `@raw_body`) while `topic`, `shop`, `api_version`, and `webhook_id` are all read from unsigned HTTP headers via `shopify_header` in `lib/shopify_api/webhooks/request.rb`. `Registry.process` validates only the HMAC over the body and then trusts `request.shop`/`request.topic` unconditionally when dispatching to handlers.

### Title
Webhook shop/topic identity headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never part of the HMAC-signed content. `Registry.process` accepts any request whose HMAC matches the body, then dispatches to the app's handler using these unverified header values as the trusted shop/topic identity.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, to_signable_string)` and compares it to the `hmac` value. [1](#0-0) 
For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, and `hmac` is parsed from the `X-Shopify-Hmac-Sha256` header, while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from separate, unsigned headers via `shopify_header`. [2](#0-1) 
`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body integrity) before using `request.topic` to look up the handler and passing `request.shop` straight into `WebhookMetadata` for the handler to act on. [3](#0-2) 

The identity binding that should hold is: `shop value trusted by the handler == shop that produced the HMAC-signed bytes`. Because the header carrying `shop` (and `topic`/`webhook_id`) is outside `to_signable_string`, this equality does not actually hold — the HMAC only proves the body bytes came from the secret holder (Shopify), not that the accompanying `shop-domain` header is bound to that same body. An unprivileged user who can obtain any single genuine webhook delivery for a shop they control (e.g., by installing a public app on their own store and having it POST a webhook to an endpoint they observe/relay) possesses a valid `(raw_body, hmac)` pair. They can then replay that exact body/hmac pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`) with a victim shop's domain or a different topic. `HmacValidator.validate` will still return true because it only re-derives the signature over `raw_body`, and `Registry.process` will hand the forged `shop`/`topic` to the registered handler as if it were authentic data for that shop/topic.

### Impact Explanation
This breaks the cross-tenant boundary the webhook verification is supposed to enforce: an attacker who is a legitimate (even free/unprivileged) user of the app on their own store can make the app believe a webhook event happened for an arbitrary victim shop domain, or reclassify it under an arbitrary topic. Any host logic keyed off `WebhookMetadata#shop` or `#topic` (e.g., data deletion flows for GDPR mandatory topics, per-shop state updates, billing/plan triggers) can be spoofed cross-tenant, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any attacker who can install the app (even on a trial/dev store) and capture one legitimate webhook delivery — no access token, `client_secret`, or privileged account is required, only the ability to relay an HTTP POST with modified headers to the app's public webhook endpoint.

### Recommendation
Include the `shop`, `topic`, and any other header-derived identity fields in the value that is HMAC-verified (or independently bind/verify the shop header against the session/install record before trusting it), rather than only signing the raw body in `to_signable_string`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a genuine webhook POST (raw body `B`, header `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker.myshopify.com`).
2. Replay the same `raw_body: B` and `hmac-sha256: H` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally change `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H`, passing validation. [4](#0-3) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", ...)`, believing the event genuinely originated from the victim shop. [5](#0-4)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
