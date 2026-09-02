### Title
Webhook `topic`/`shop`/`webhook_id`/`api_version` are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds its HMAC verification exclusively to the raw request body, while the `topic`, `shop`, `webhook_id`, and `api_version` fields — used by `Registry.process` to route the payload and identify the tenant — are read straight from caller-supplied HTTP headers with no cryptographic tie to the verified bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC solely against that signable string [2](#0-1) . Meanwhile `topic`, `shop`, `webhook_id`, and `api_version` are parsed from HTTP headers that are not part of the signed material at all [3](#0-2) .

`Registry.process` verifies the HMAC and then immediately trusts `request.topic` and `request.shop` (header-derived) to route to a handler and construct `WebhookMetadata`, which is handed to the app's business logic as the authoritative tenant/topic identity: [4](#0-3) .

This breaks the intended identity binding: `hmac(raw_body) == valid` should imply `(shop, topic) == the shop/topic that produced this exact body`, but the gem only proves the body was HMAC'd with the app's secret — it proves nothing about which shop or topic header accompanies it. Since the same `client_secret` is shared across all shop installations of a given app, anyone who has captured one legitimately-delivered webhook (body + `x-shopify-hmac-sha256`) for *their own* shop — which requires no special privilege beyond installing/using the app on their own store — can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` header values. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will route it to whichever handler matches the attacker-chosen topic and pass along the attacker-chosen `shop` in `WebhookMetadata`.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` (or `#topic`) from `Registry.process` to select which tenant's data to update, delete, or act upon (a very common and directly documented usage pattern) can be tricked into performing that action against a different shop than the one that actually generated the payload — a cross-tenant data-integrity/access issue. This meets the "cross-tenant access" criterion for Critical impact, since the gem's own header-trust-without-binding is the direct root cause, not a documented misuse.

### Likelihood Explanation
Exploitation requires only: (1) the attacker controls or has visibility into webhook deliveries for at least one shop that installed the target app (trivial for any public app — attacker installs their own dev store), and (2) the attacker can send arbitrary HTTP requests to the app's public webhook endpoint (also trivial, since these endpoints are internet-facing by design). No `api_secret_key`, access token, or privileged account is needed — the attacker never learns the secret, they only replay a body+HMAC pair they were legitimately shown, with swapped headers. This is a realistic, low-effort attack path.

### Recommendation
Bind the header-derived identity fields into the HMAC-signed material, or independently authenticate them:
- Include `shop`, `topic`, and `webhook_id` in the signable string that `HmacValidator` verifies (mirroring how `Oauth::AuthQuery#to_signable_string` folds `shop`, `host`, `state`, etc. into one signed blob [5](#0-4) ), so a mismatch between the signed body and the asserted shop/topic causes HMAC validation to fail.
- Alternatively, cross-check the header `shop`/`topic` against the corresponding fields embedded in the parsed JSON body (Shopify webhook payloads typically include shop/domain identifiers) before dispatching to a handler.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker-shop.myshopify.com` (no special privilege required).
2. Attacker triggers any subscribed webhook (e.g., `orders/create`) on their own shop and captures the raw POST body and its `x-shopify-hmac-sha256` header from Shopify's delivery.
3. Attacker replays that exact `(raw_body, hmac)` pair to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: shop/redact` (or any other registered topic).
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully [6](#0-5) , `Utils::HmacValidator.validate(request)` returns `true` because only the (unchanged) body is checked [2](#0-1) , and `Registry.process` dispatches `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", body: ..., ...)` to the app's handler [4](#0-3) , causing the app to act on `victim-shop` using attacker-controlled body content.

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
