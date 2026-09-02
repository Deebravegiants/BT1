This confirms the analog. Comparing `AuthQuery#to_signable_string` (which binds `code`, `host`, `shop`, `state`, `timestamp` all into the signed string) against `Webhooks::Request#to_signable_string`, which returns only `@raw_body` — the `topic`, `shop`, `api_version`, and `webhook_id` headers are parsed and acted upon but never enter the HMAC computation.

### Title
Webhook HMAC Does Not Cover `shop`/`topic`/`webhook-id` Headers, Enabling Cross-Tenant Webhook Forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks the signature against `verifiable_query.to_signable_string`, i.e. the body [3](#0-2) . `Registry.process` accepts the request once this body-only HMAC passes, then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values [4](#0-3) .

### Finding Description
The equality this gem is supposed to enforce is: **bytes verified by HMAC == bytes the application acts on**. For the OAuth callback, this holds — `AuthQuery#to_signable_string` folds `code`, `host`, `shop`, `state`, and `timestamp` into one signed string [5](#0-4) , so none of those fields can be altered without invalidating the signature. For webhooks, this equality is broken: the signed bytes are `raw_body` alone, but `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight out of the `x-shopify-*`/`shopify-*` headers with no cryptographic binding to that body [2](#0-1) .

Any unprivileged internet user who can obtain one valid `(raw_body, hmac)` pair — trivially available by installing the target app on their own shop and receiving one legitimate webhook — can replay that exact body/HMAC to the app's public webhook endpoint while substituting arbitrary `shop-domain`, `topic`, `webhook-id`, and `api-version` header values. `HmacValidator.validate` recomputes the signature over the unchanged body and secret, so it still succeeds [6](#0-5) , and `Registry.process` will hand the forged `shop`/`topic`/`webhook_id` straight to the app's handler as `WebhookMetadata` [7](#0-6) . Because host applications commonly key their per-tenant session/data lookup off `WebhookMetadata#shop` (this is the documented/intended field per the gem's own API), an attacker can make the app believe attacker-controlled webhook data belongs to an arbitrary victim shop, and/or trigger a different topic handler than the one Shopify actually fired.

### Impact Explanation
This is a cross-tenant identity-binding break carrying the app's own trusted verification path (the HMAC check the gem exposes as its security boundary for webhooks). An attacker who legitimately installs the app on their own shop (unprivileged, no special access to any other merchant) can forge webhook deliveries that the app's `HmacValidator` accepts as authentic, but attributed to any shop domain and any topic of the attacker's choosing — a direct cross-tenant access vector through the gem's core webhook-verification API.

### Likelihood Explanation
Webhook endpoints are, by design, public unauthenticated HTTP endpoints that must accept unauthenticated POSTs from Shopify's infrastructure; nothing about the endpoint itself gates a well-formed forged request. Obtaining a valid `(body, hmac)` pair requires nothing more than installing the target app on any shop (including the attacker's own), which is the normal, expected, low-privilege interaction with a Shopify app. No secrets, tokens, or elevated access are required.

### Recommendation
Bind the identifying headers into the HMAC-verified material for webhooks the same way `AuthQuery` does for OAuth: include `shop-domain`, `topic`, `webhook-id`, and `api-version` in `to_signable_string` (or perform a second, explicit comparison confirming the header values match what the handler is told), so `HmacValidator.validate` fails whenever any header is altered independent of the body's signature.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver one legitimate webhook, capturing `raw_body` and the `x-shopify-hmac-sha256` header — both valid and Shopify-signed.
2. Attacker POSTs to the app's webhook endpoint with the exact same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: <different-topic>`.
3. `ShopifyAPI::Webhooks::Request.new` parses these forged headers without validation [8](#0-7) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and succeeds since the body/secret/HMAC triple is unchanged [9](#0-8) .
5. The registered handler for the (possibly forged) topic executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload actually originated from and pertains to the attacker's own shop [7](#0-6) .

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
