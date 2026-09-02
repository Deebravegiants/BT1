### Title
Webhook HMAC covers only the raw body, not the `shop`/`topic` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the value that gets HMAC-verified from the raw request body alone, while `shop`, `topic`, `webhook_id`, and `api_version` are taken from unauthenticated HTTP headers and are handed directly to the registered webhook handler after the HMAC check passes. The signature never binds the header-derived `shop`/`topic` to the payload, so anyone who can obtain one valid `(body, hmac)` pair signed with the app's shared `api_secret_key` can replay that pair with a different `Shopify-Shop-Domain`/`Shopify-Topic` header and have the app process it as if it belonged to another merchant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers, with no cryptographic tie to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature by hashing only `to_signable_string` (i.e., the raw body) with the app's secret and comparing to the `hmac` header: [3](#0-2) 

`Webhooks::Registry.process` accepts the request once that body-only HMAC passes, then forwards the *header-derived* `shop` and `topic` values, unauthenticated, straight to the app's business-logic handler: [4](#0-3) 

This breaks the intended identity binding: `shop authenticated by HMAC == shop the handler acts on`. Because `api_secret_key` is the single app-level client secret shared by Shopify across **every merchant** that installs the app (not a per-shop secret), any merchant who has installed the app can trigger a real event in their own store to obtain one legitimately-signed `(raw_body, hmac)` pair from Shopify, then resend that exact body/HMAC to the app's public webhook endpoint while swapping the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header to name a different, victim shop. Since those headers are never part of the signed material, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` will invoke the handler with `shop: <victim-shop>`, `topic: <attacker-chosen-topic>` and the attacker's body content.

### Impact Explanation
This is a cross-tenant boundary break: an attacker (any merchant using the shared app, i.e. an "unprivileged" party relative to other tenants of the app, with no access to the app's `client_secret`, no TLS interception, and no privileged account) can make the app process webhook events attributed to a completely different shop. Depending on how the host application's webhook handlers act on `shop`/`topic` (e.g., updating billing/subscription state, deleting data, changing app configuration, disabling features, or writing to that shop's session/store), this can lead to unauthorized cross-tenant data modification or state changes performed under another merchant's identity — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires no secret material beyond what any merchant using the app already legitimately receives (a real webhook fired by their own store), and no special network position — only the ability to send an HTTP POST to the app's public webhook endpoint with a forged header. This is straightforward for any user who has installed the target app in their own Shopify store.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `api_version`, `webhook_id`) in the material that is HMAC-verified — e.g., verify the raw body as Shopify does, but additionally require and check that the `shop` value in the header matches the shop the webhook was registered for/expected, or bind these values cryptographically before trusting them in `Registry.process`. At minimum, document and enforce that `Webhooks::Registry.process` must not trust the header-derived `shop`/`topic` for authorization decisions unless independently corroborated (e.g., cross-checked against the session/store the webhook was registered against).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers webhook topic `orders/create` (or any topic the app handles).
2. Attacker creates an order in their own store, causing Shopify to POST a webhook to the app's endpoint with a real body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this HMAC is computed over the body only, per `Request#to_signable_string`/`HmacValidator`.
3. Attacker captures `(B, H)` (e.g., via their own logging/proxy of their own webhook traffic — no secret needed).
4. Attacker replays a POST to the same public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
5. `Utils::HmacValidator.validate(request)` returns `true` because it only hashes `B`. `Webhooks::Registry.process` then invokes the registered handler with `shop: "victim-shop.myshopify.com"`, letting the attacker's chosen body be processed as an authentic event for the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
