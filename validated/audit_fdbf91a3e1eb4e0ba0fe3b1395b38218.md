### Title
Webhook HMAC only covers the raw body, so the `shop` domain and `topic` used for tenant routing are forgeable - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` cryptographically authenticates the request **body bytes only**. The `shop`, `topic`, `webhook_id`, and `api_version` values that `ShopifyAPI::Webhooks::Registry.process` uses to identify the tenant and dispatch the handler are pulled straight from unauthenticated HTTP headers, which are never included in the signed string.

### Finding Description
`Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` purely from raw headers: [1](#0-0) 
but the signable payload used for HMAC verification is only the body: [2](#0-1) 

`Registry.process` trusts `Utils::HmacValidator.validate(request)` as proof the "request did indeed come from Shopify" (per the gem's own docs), and then immediately uses the unauthenticated `request.shop` and `request.topic` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature strictly from `to_signable_string`, i.e. the body only, using the app's single, shop-independent `Context.api_secret_key`: [4](#0-3) 

The identity binding that should hold is:
`HMAC-authenticated bytes == bytes that determine the tenant (shop) and event (topic) trusted by the handler`

Here that equality is broken: the HMAC only binds the body; `shop`/`topic`/`webhook_id` are parsed from headers that sit entirely outside the signed string. Because the webhook-signing secret (`api_secret_key`, the app's `client_secret`) is the same for every shop that installs the app, any merchant who legitimately installs the app receives genuine `(raw_body, hmac)` pairs signed with that shared secret. That merchant (an unprivileged internet user relative to other tenants) can replay the exact same body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header for a victim shop, and `HmacValidator.validate` will still succeed since it never inspects those headers.

The documentation for this exact API explicitly states this call "will verify the request did indeed come from Shopify," reinforcing that host apps are meant to rely on `Registry.process` for full authenticity of `data.shop`/`data.topic`, not just the body: see `docs/usage/webhooks.md` lines 125 and 12-17 (fields `topic`, `shop` presented as verified webhook metadata).

### Impact Explanation
This is a cross-tenant boundary violation: an app relying on `ShopifyAPI::Webhooks::Registry.process` to authenticate incoming webhooks will accept attacker-forged `shop`/`topic` values as if Shopify itself vouched for them, because the gem's own documented processing method conflates "HMAC-verified" with "fully authenticated webhook metadata." Downstream handlers (as shown in the gem's own example, `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process/store data keyed to a `shop` value that was never cryptographically bound to the signed bytes, enabling cross-tenant data injection into another merchant's records.

### Likelihood Explanation
Any user who can install the app on their own shop already legitimately receives valid `(raw_body, hmac)` webhook deliveries signed with the app's shared `client_secret`. No access to the app's secret or another merchant's credentials is needed — only a normal HTTP POST to the public webhook endpoint with a substituted shop-domain header and the previously-observed valid body/HMAC pair.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the HMAC-signed material, or independently verify that `request.shop` corresponds to a shop with a valid, previously-established session/installation before trusting it in `Registry.process`. At minimum, document prominently that `Registry.process` only authenticates the body and that callers must independently verify the shop-domain header against known installed shops.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets Shopify deliver a real webhook, capturing the exact `raw_body` and its `shopify-hmac-sha256` header (both valid, since they're signed by the app's shared `client_secret`).
2. Attacker sends a forged POST to the app's webhook route with the same `raw_body`/`hmac` but header `shopify-shop-domain: victim.myshopify.com` (and optionally a different `shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses these headers verbatim [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `raw_body` [6](#0-5) .
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"`, which the host app treats as an authentic event for the victim tenant.

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
