### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted but not covered by the HMAC signature, breaking the shop-identity binding - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` as attributes read directly from HTTP headers, but `to_signable_string` — the value that `Utils::HmacValidator.validate` actually verifies — is only the raw request body. The HMAC therefore authenticates the body's integrity/origin but never binds the `shop-domain` header to that signature, so `request.shop` can be swapped by anyone able to replay a validly-signed webhook payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` treats a passing `HmacValidator.validate(request)` call as proof the whole webhook request is authentic, then forwards `request.shop` (read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header) to the handler: [3](#0-2) [4](#0-3) 

Because Shopify signs webhooks with the **app's** `client_secret` (identical across every shop that installs the app) rather than a per-shop key, and only the body bytes are covered by that signature, an unprivileged user who controls (or installs the app on) any shop can capture one of their own genuinely-signed webhook deliveries and re-POST it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a different (victim) shop. `Utils::HmacValidator.validate` still returns `true` (the body and its HMAC are untouched), yet `WebhookMetadata.shop` now reports the attacker-chosen shop. This breaks the identity binding: `shop claimed in header == shop that actually produced the HMAC-covered bytes`.

### Impact Explanation
Apps built on this gem commonly key per-tenant behavior (session/config lookup, data writes, state changes) off `WebhookMetadata#shop`, trusting it because it arrives alongside a "validated" webhook. Since the gem's own verification primitive (`HmacValidator` + `Webhooks::Request`) never binds `shop` to the signature, an attacker can make the host application attribute attacker-controlled webhook content to an arbitrary victim shop — a cross-tenant boundary break rooted entirely in this gem's code path, not host misuse.

### Likelihood Explanation
Any actor able to install the app on a shop they control (a normal, unprivileged flow for public/embedded Shopify apps) receives real webhooks with valid HMACs for arbitrary topics on demand, and only needs to change one header to target another tenant. No access token, `client_secret`, or privileged access is required — this is directly reachable via the gem's public `Registry.process` API.

### Recommendation
Include the shop domain (and other headers the application logic depends on, e.g. topic/webhook id) inside the HMAC-covered signable string, or otherwise cryptographically bind the header values to the signed payload (e.g., derive/verify `shop` from a value embedded in the signed body, or require an out-of-band verified mapping of shop → webhook subscription id) rather than trusting header values whose signature only covers the request body.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), capturing the legitimate raw body and its `x-shopify-hmac-sha256` value from Shopify.
2. Attacker replays this exact body + HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header fine (headers aren't validated for authenticity, only presence) — see the constructor's header check: [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (untouched) raw body against the (untouched) HMAC.
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload/signature originated from `attacker.myshopify.com`, letting the attacker inject or forge webhook-triggered behavior attributed to a shop they don't control.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
```ruby
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
