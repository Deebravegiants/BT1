### Title
Webhook shop/topic identity headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are read from unauthenticated HTTP headers that are never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (the raw body) against `verifiable_query.hmac` (derived from the `hmac-sha256` header): [3](#0-2) 

`Registry.process` then uses the *unsigned* `request.topic` to pick the handler and passes the *unsigned* `request.shop` straight into the payload delivered to the app's business logic: [4](#0-3) 

This breaks the intended identity binding: `hmac == HMAC(body)` is verified, but the code then trusts `shop-header == actual originating shop` and `topic-header == actual event type`, neither of which the HMAC covers. Because Shopify uses the **same** `api_secret_key` to sign every shop's webhook body for a given app, an attacker who controls (or has installed the app on) *any* shop, call it shop A, can generate an arbitrarily-bodied webhook (e.g., a `customers/create` payload with attacker-chosen JSON) with a valid HMAC for that body. The attacker then replays that exact `body` + `hmac-sha256` header to the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop B (and/or the `x-shopify-topic` header to a different registered topic). `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` hands the handler `WebhookMetadata.new(topic: <attacker-chosen>, shop: "shop-B", body: <attacker-chosen JSON>, ...)` — the app now believes attacker-controlled data legitimately originated from shop B.

### Impact Explanation
This is a cross-tenant confusion primitive: the receiving app's webhook handlers key their persistence/business logic off `data.shop` (this is the documented contract of `WebhookMetadata`), trusting it as the authenticated tenant identity. An attacker with a webhook-capable shop of their own can forge webhooks that appear to originate from any other shop, with attacker-chosen topic and body content, satisfying the "cross-tenant access" criterion for Critical/High severity in the rules (tenant identity — the `shop` field — is acted upon but not covered by the HMAC that is meant to authenticate the request).

### Likelihood Explanation
Exploitation requires only: (1) the ability to send an arbitrary HTTP POST to the target app's public webhook endpoint (any unprivileged internet user, since webhook endpoints are public HTTP endpoints by design), and (2) a legitimately-signed body+hmac pair, which the attacker can trivially obtain by installing the same app on a shop they control (a normal, unprivileged action for any Shopify Partner/dev store) and capturing one real webhook delivery, or by locally reproducing any topic/body they want to forge since the secret used is the app's single, shop-independent `api_secret_key` — no leaked credentials or privileged account access needed. This satisfies the "does not require access token/api_secret_key leak" scoping constraint since it relies only on the gem's own webhook processing logic, not on defeating cryptography.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signable string, or otherwise cryptographically bind them to the payload, so that `to_signable_string` in `lib/shopify_api/webhooks/request.rb` cannot be desynchronized from the values `Registry.process` uses for routing and tenant attribution. At minimum, document and/or enforce that these header values must not be trusted as authenticated unless additionally verified out-of-band (e.g., against the resolved session/shop store), and consider rejecting/logging any mismatch between the shop implied by body content (if derivable) and the `shop-domain` header.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and triggers/observes a real webhook delivery, capturing `raw_body` and the `x-shopify-hmac-sha256` header (both valid since HMAC is computed only over the body with the app's shared `api_secret_key`).
2. Attacker crafts a POST to the app's webhook endpoint reusing that exact `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and (optionally) a different `x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers successfully (all required headers present) — [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `hmac` against `raw_body` — [6](#0-5) .
5. The handler registered for the (possibly attacker-chosen) topic receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, and the app's business logic acts on it believing it is authentic data from the victim tenant — [7](#0-6) .

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
