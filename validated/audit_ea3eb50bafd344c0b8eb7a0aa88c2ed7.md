### Title
Webhook shop/topic/webhook-id are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by calling `Utils::HmacValidator.validate(request)` and, if it passes, immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` object passed to the app's handler: [1](#0-0) 

The problem is that the HMAC signature only covers the raw request body, not the headers that carry the shop, topic, and webhook id: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature strictly against `verifiable_query.to_signable_string`, which for `Request` is just `@raw_body`: [3](#0-2) 

So the binding that should hold is:
`HMAC-verified bytes == bytes that determine tenant identity (shop) and semantics (topic, webhook_id)`

In this gem that equality does not hold: the HMAC only proves "this body was produced using the app's `api_secret_key`" — it says nothing about which shop or topic the body belongs to, because `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers (`shopify_header` in `Request`).

### Impact Explanation
Because the app's `api_secret_key` is shared across every shop that has the app installed, an unprivileged attacker who controls (or can trigger a webhook delivery to) their own low-privilege installation can capture one legitimately-signed `(raw_body, hmac)` pair. They can then replay that exact body/HMAC pair directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with a victim shop's identifier. `HmacValidator.validate` will still pass (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop/topic. Any host application that uses `WebhookMetadata#shop` to key into its per-tenant data store, update tenant-scoped records, or invalidate/refresh tenant sessions will act on attacker-chosen data under an incorrect tenant identity — a cross-tenant confusion / spoofing condition rooted entirely in this gem's verification logic, matching the report's bug class of "field acted upon but not covered by the HMAC."

### Likelihood Explanation
Likelihood is realistic but not trivial: the attacker needs a legitimately signed body from any shop that has the app installed (achievable via a low-cost/dev store installation of the target app) and must know or guess the app's public webhook endpoint URL. No access token, `api_secret_key`, or privileged account is required — only a normal, unprivileged install of the target app, which satisfies the "unprivileged internet user" threat model.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body, so `Registry.process` cannot report a shop/topic to the handler that wasn't part of what was actually authenticated by Shopify for that specific delivery.

### Proof of Concept
1. Install the target app on an attacker-owned shop `attacker-shop.myshopify.com`; trigger any webhook topic the app subscribes to (e.g. `orders/create`) and capture the raw POST: body `B` and header `x-shopify-hmac-sha256: S` (where `S = HMAC-SHA256(api_secret_key, B)`), per `Request#hmac`/`#to_signable_string` at [4](#0-3) .
2. Send a new POST request to the app's public webhook endpoint reusing body `B` and header `x-shopify-hmac-sha256: S` unchanged, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against `S` — this succeeds, per [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data under the victim shop's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
