### Title
Webhook Shop/Topic/ID Headers Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, while the `shop`, `topic`, and `webhook_id` values that the handler actually acts on are read from HTTP headers that are never covered by that signature. An attacker who can obtain one genuine, validly-signed webhook body (e.g. by installing the target app on a shop they control) can replay that exact body while substituting the `x-shopify-shop-domain` (and/or topic/webhook-id) header for a victim shop, and the request still passes HMAC validation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from request headers, none of which participate in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac-sha256` header — i.e. it only proves the body bytes are authentic, not the header metadata: [3](#0-2) 

`Registry.process` checks that HMAC and then hands the *header-derived* `shop`, `topic`, and `webhook_id` straight to the app's handler as trusted metadata describing the webhook's tenant/origin: [4](#0-3) 

The identity binding that should hold is: `shop header == shop that Shopify actually authenticated the body for`. Before an attack, this holds because Shopify's own dispatcher sets both consistently. After the attacker's request, the equality breaks: the HMAC only proves "this body was produced with our `api_secret_key`" (true for *any* shop that has installed the app, since `api_secret_key` is shared across all shop installations of the app) — it proves nothing about which shop's `x-shopify-shop-domain` header should accompany that body. An attacker who installs the target app on their own shop receives genuine, validly signed webhooks. They can then send a forged HTTP request to the app's webhook endpoint using that captured `(raw_body, hmac)` pair, but with the `shop-domain` header (and/or `topic`/`webhook-id`) rewritten to point at a different, victim shop. `Utils::HmacValidator.validate` still returns `true` (it only checked the body), and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This is a cross-tenant boundary break: an app that uses `shop:` from `WebhookMetadata` to select which merchant's session/data to update (a standard pattern per the gem's documented webhook usage) can be tricked into writing/processing attacker-supplied webhook content under a victim shop's identity, without ever compromising the victim or the app's secret. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be an ordinary (unprivileged) internet user who can install the target's public app on a shop they control — a routine, unprivileged action — and then send one crafted HTTP request with headers of their choosing. No access token, `api_secret_key`, or victim credentials are required.

### Recommendation
Bind the header-derived identity fields into the signed material, or independently verify them: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (matching how Shopify's newer webhook verification recommends validating headers together with the body), or, at minimum, require the caller to supply the expected shop/topic out-of-band and reject mismatches before invoking `handler.handle`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H = HMAC(api_secret_key, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays this exact `(B, H)` pair to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and matches `H` — validation succeeds.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and processes attacker-controlled content as if it were authoritative data from the victim shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
