I have enough evidence to finalize the analysis. The webhook `Request#hmac` only signs `@raw_body` via `to_signable_string`, while `topic`, `shop`, `webhook_id`, and `api_version` come from unauthenticated HTTP headers that are never part of the signed bytes, yet `Registry.process` trusts `request.shop` for tenant dispatch after HMAC "validation" succeeds.

### Title
Webhook `shop`/`topic` identity headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated for a specific shop and topic once `Utils::HmacValidator.validate(request)` returns `true`. However, the HMAC only signs the raw request body, not the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers that the registry and handler actually act on.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: `@raw_body`. [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` value taken from the `hmac-sha256` header: [2](#0-1) 

`Registry.process` gates dispatch solely on that HMAC check, then builds `WebhookMetadata` from `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version`, all of which are read directly from HTTP headers with no cryptographic binding to the signed body: [3](#0-2) [4](#0-3) [5](#0-4) 

Because the signature only proves "this exact body was signed with the shared secret at some point," and not "this body belongs to shop X and topic Y," anyone in possession of one legitimate `(raw_body, hmac)` pair — for example a webhook the attacker's own store received, or one leaked/logged/replayed from any source — can resend that same body with a different `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` header. `HmacValidator.validate` will still return `true` because it only recomputes the HMAC over `@raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the attacker-chosen shop/topic. This breaks the identity binding: **bytes verified (raw body) ≠ bytes/fields acted on (shop, topic, webhook_id headers)**.

### Impact Explanation
This enables cross-tenant confusion in the receiving application: a webhook handler that uses `WebhookMetadata#shop` to route or persist data for a specific merchant can be tricked into applying a legitimately-signed payload to a different shop's context (e.g. spoofing which shop's `orders/create` or `app/uninstalled` event just fired), or into re-labeling the topic so the wrong handler logic processes attacker-influenced but genuinely-signed data. Since `shop` is the only tenant identifier passed out of this gem's webhook layer, and it is not covered by the signature this gem itself validates, this is a cross-tenant boundary break rooted entirely in this gem's design (`Registry.process` + `Request`), independent of how any host app happens to use the callback.

### Likelihood Explanation
Exploitation requires possession of at least one legitimate `(raw_body, hmac)` pair, which is trivial for an attacker who owns/installs the app on their own development shop (they don't need the secret — Shopify signs and delivers the webhook to the app's endpoint for their own shop's events). If the attacker can intercept/replay that request to the app endpoint with altered headers, the header fields are never checked against the signature. This is a structural signature-coverage gap in the gem, not a theoretical edge case.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (all values the app relies on for authorization/routing) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document that the HMAC covers the body only and that hosts must independently corroborate `shop`/`topic` (e.g., against the session/shop that is expected for that webhook subscription) before acting on the metadata.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, gets a real webhook (e.g., `orders/create`) delivered to the app's registered endpoint with a valid `shopify-hmac-sha256` header computed over the JSON body using the shared `api_secret_key`.
2. Attacker captures the raw body + `hmac-sha256` header value (e.g., via their own logging proxy in front of their self-hosted app instance, or a shared testing environment).
3. Attacker resends the exact same raw body and HMAC header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `shopify-topic`/`shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not consistency): [6](#0-5) 
5. `Utils::HmacValidator.validate(request)` returns `true` because it only hashes `@raw_body`, unaffected by the header change.
6. `Registry.process` dispatches to the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", ...)`, and the handler now believes the (genuinely-signed) payload originated from and applies to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
