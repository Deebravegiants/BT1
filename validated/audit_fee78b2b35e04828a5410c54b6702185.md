Based on my investigation, I found a valid analog.

### Title
Webhook shop identity spoofing via HMAC not covering the shop-domain header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` computes the webhook HMAC over the raw body only, while the `shop` value dispatched to the application's webhook handler is taken from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header. This breaks the identity binding `shop authenticated == shop used by the handler`, letting a party who legitimately received one valid `(body, hmac)` pair replay it against the same endpoint while claiming it belongs to an arbitrary other shop.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the (attacker-controllable, replayable) header, entirely outside the signed content: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e., only the body is checked - it never binds `shop` (or `topic`/`webhook_id`/`api_version`) into the signature: [3](#0-2) 

`Registry.process` validates the HMAC and then hands `request.shop` (the raw, unauthenticated header value) straight to the registered handler as trusted webhook metadata: [4](#0-3) 

The `api_secret_key` used to sign webhooks is the app's single shared secret across every shop that installs it (same key used in `HmacValidator.validate`), not a per-shop secret. Consequently any shop that has the app installed - an unprivileged internet user in the sense that they only control their own store - receives genuine `(body, hmac)` pairs signed with that same shared secret. Nothing in the library prevents them from re-POSTing that exact `raw_body` + `hmac` to the app's webhook endpoint with a forged `shopify-shop-domain` header naming a different, victim shop. `HmacValidator.validate` still returns `true` (the body/hmac pair is genuine), and `Registry.process` will dispatch the payload to the handler tagged with the attacker-chosen `shop`, breaking the equality `shop bound by HMAC == shop trusted by handler`.

This is different from `ShopifyAPI::Auth::Oauth::AuthQuery`, where the equivalent field (`shop`) is explicitly included in `to_signable_string` and therefore is bound to the signature: [5](#0-4) 

The webhook path has no equivalent binding for `shop`, `topic`, or `webhook_id`.

### Impact Explanation
An attacker who is a legitimate (even trial/free) merchant of the same app can forge the shop attribution of a webhook payload delivered to the app's own backend, causing the application to process/store data (e.g., orders, customer PII, redact requests) under a victim shop's identity — a cross-tenant data-integrity/confidentiality break. Because handlers built on top of `WebhookMetadata`/`Registry.process` are told to trust `data.shop` once `HmacValidator.validate` succeeds, this crosses the tenant boundary the gem is expected to enforce.

### Likelihood Explanation
Requires only: (1) installing the app once on an attacker-controlled shop to capture a genuine `(raw_body, hmac)` pair for a chosen topic, and (2) network access to POST to the app's public webhook endpoint with a forged shop-domain header — both are unprivileged, no leaked secrets or tokens required.

### Recommendation
Bind the shop identity (and ideally topic/webhook id) into the value that is cryptographically verified — e.g., have `Request#to_signable_string` incorporate the `shop`, `topic`, and `webhook_id` header values alongside the raw body (mirroring what `AuthQuery#to_signable_string` already does for OAuth), or have `Registry.process` independently confirm that `request.shop` corresponds to a shop with an active registration/session before dispatching to the handler.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; Shopify sends a webhook (e.g., `orders/create`) with body `raw_body` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, raw_body)`.
2. Attacker re-sends an HTTP request to the app's public webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (= `raw_body`) and matches `H` — validation passes.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...))`, causing the application to treat the attacker's payload as authentic data for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
