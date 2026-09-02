### Title
Webhook HMAC only signs the request body, letting any tenant using the same app forge webhook events (shop, topic, webhook_id) for a different shop - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` purely from unauthenticated HTTP headers, while `to_signable_string` (the value actually covered by the HMAC signature) is only the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts the header-derived `shop`/`topic` after validating only that the body's HMAC is correct, exactly mirroring the reported bug class: one value (the body) is cryptographically authenticated, but a different, unbound value (the shop/topic headers) is what the code actually acts upon — an assumption that the two are tied together which does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all read straight from HTTP headers, with no cryptographic binding to the body or its signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(api_secret_key, to_signable_string)`, i.e., only the body bytes: [3](#0-2) 

`Registry.process` performs this HMAC check and then immediately hands the *header-derived* `shop`/`topic`/`webhook_id` to the app's handler, with no verification that they correspond to the signed body: [4](#0-3) 

Because `Context.api_secret_key` is the single shared secret for the whole app (used to sign webhooks for *every* installed shop, not one secret per shop), any merchant who has installed the app can trigger a legitimate webhook on their own shop, capture the resulting `(raw_body, hmac)` pair — which they fully control the timing and, within the JSON schema, content of — and replay that exact `raw_body`/`hmac` to the app's webhook endpoint while substituting the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers with a victim shop's identifiers. The HMAC check still passes because it only verifies the body bytes, and `Registry.process` will invoke the topic handler with `shop: <victim-shop>`.

This is the exact analog of the `OracleRef` bug: the code assumes that because the *body* is authenticated, the *header claims* attached to it are equally trustworthy, when in fact nothing binds them together.

### Impact Explanation
This breaks the identity binding `HMAC-authenticated origin == shop the handler acts on`. A malicious/compromised tenant can spoof webhook events attributed to any other shop using the same app, causing the host application's webhook handler to process attacker-controlled data under another merchant's identity — a cross-tenant access/data-confusion primitive (e.g., an app that syncs orders, cancels subscriptions, or updates local per-shop state keyed by `webhook.shop` could have its per-tenant data corrupted or manipulated by another tenant). This falls under the "cross-tenant access" High/Critical impact category.

### Likelihood Explanation
Likelihood is realistic for any app builder using this library that installs on multiple, mutually-untrusting merchants (the common SaaS app model): any one of those merchants is an "unprivileged" attacker relative to the others, can install the app on their own store to obtain valid `(body, hmac)` pairs, and can send arbitrary HTTP requests to the app's public webhook endpoint with forged headers. No secrets, tokens or elevated privileges beyond "being a customer of the app" are required.

### Recommendation
Bind the claimed `shop` (and ideally `topic`/`webhook_id`) into the value that is actually HMAC-verified, e.g., include the `shopify-shop-domain` header (and topic) in `to_signable_string`, or independently verify that the `shop` header matches a shop known to have an active, matching webhook subscription/session before invoking the handler. At minimum, document that the current implementation does not cryptographically bind the reported `shop`/`topic` headers to the signed payload, and require host apps to cross-check `shop` against their own webhook subscription/session records.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a real webhook (e.g. `orders/create`), receiving from Shopify a POST with body `B` and header `x-shopify-hmac-sha256: H = HMAC(api_secret_key, B)`.
2. Attacker replays a request to the app's webhook endpoint with the same body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and any desired `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers verbatim: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes `HMAC(api_secret_key, B)` and compares it to `H` — the spoofed `shop-domain` header is never inspected by the validator.
5. The registered handler is invoked with `shop: "victim.myshopify.com"`, `body: JSON.parse(B)`, executing app logic under the victim shop's identity despite the request having nothing to do with that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
